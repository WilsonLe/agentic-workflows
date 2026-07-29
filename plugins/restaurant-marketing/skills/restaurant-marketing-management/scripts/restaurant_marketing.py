#!/usr/bin/env python3
"""Validate and summarize restaurant marketing records without external services."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

MAX_RECORD_BYTES = 2 * 1024 * 1024
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
UTM_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(?:\+?\d[\s().-]*){8,}")

ARCHETYPES = {
    "new_dish",
    "offer",
    "seasonal_dish",
    "event",
    "slow_period",
    "local_discovery",
    "reputation",
    "retention",
    "opening_relaunch",
}
PLAN_STATUSES = {
    "draft",
    "blocked",
    "ready_for_approval",
    "approved",
    "scheduled",
    "live",
    "paused",
    "closed",
    "withdrawn",
}
CLAIM_TYPES = {
    "factual",
    "price",
    "savings",
    "scarcity",
    "health",
    "dietary",
    "allergen",
    "origin",
    "sustainability",
    "award",
    "popularity",
    "testimonial",
}
HIGH_RISK_CLAIMS = CLAIM_TYPES - {"factual", "price"}
MUTATING_DELIVERABLE_STATES = {"approved", "scheduled", "published", "verified"}
BASE_KEYS = {"schema_version", "record_type", "record_id", "updated_at"}
PROFILE_KEYS = BASE_KEYS | {
    "restaurant",
    "surfaces",
    "operations",
    "measurement",
    "claim_sources",
    "direct_marketing",
    "approvals",
    "unknowns",
}
PLAN_KEYS = BASE_KEYS | {
    "campaign",
    "truth",
    "economics",
    "audience",
    "message",
    "claims",
    "deliverables",
    "approvals",
    "measurement",
    "monitoring",
    "expiry",
    "compliance",
    "unknowns",
}
RESULT_KEYS = BASE_KEYS | {
    "campaign_id",
    "status",
    "closed_at",
    "observations",
    "calculations",
    "inferences",
    "unknowns",
    "decisions",
    "expiry_verified",
    "retained_evidence",
}


class RecordError(ValueError):
    """A safe, user-actionable validation error."""


def _error(path: str, message: str) -> None:
    raise RecordError(f"{path}: {message}")


def _object(value: object, path: str) -> dict[str, object]:
    if not isinstance(value, dict):
        _error(path, "must be an object")
    return value


def _list(value: object, path: str) -> list[object]:
    if not isinstance(value, list):
        _error(path, "must be an array")
    return value


def _string(value: object, path: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        _error(path, "must be a non-empty string")
    return value


def _boolean(value: object, path: str) -> bool:
    if not isinstance(value, bool):
        _error(path, "must be a boolean")
    return value


def _strict(record: dict[str, object], allowed: set[str], path: str) -> None:
    unknown = sorted(set(record) - allowed)
    if unknown:
        _error(path, f"unknown field(s): {', '.join(unknown)}")
    missing = sorted(allowed - set(record))
    if missing:
        _error(path, f"missing field(s): {', '.join(missing)}")


def _id(value: object, path: str) -> str:
    text = _string(value, path)
    if not ID_PATTERN.fullmatch(text):
        _error(path, "must match ^[a-z0-9][a-z0-9_-]{0,63}$")
    return text


def _timestamp(value: object, path: str) -> str:
    text = _string(value, path)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RecordError(f"{path}: must be an ISO 8601 date-time") from exc
    if parsed.tzinfo is None:
        _error(path, "must include a timezone")
    return text


def _date(value: object, path: str) -> str:
    text = _string(value, path)
    try:
        date.fromisoformat(text)
    except ValueError as exc:
        raise RecordError(f"{path}: must be an ISO 8601 date") from exc
    return text


def _string_list(value: object, path: str) -> list[str]:
    values = _list(value, path)
    result = [_string(item, f"{path}[{index}]") for index, item in enumerate(values)]
    if len(result) != len(set(result)):
        _error(path, "must not contain duplicates")
    return result


def _decimal(value: object, path: str, *, positive: bool = False) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        _error(path, "must be a finite decimal")
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise RecordError(f"{path}: must be a finite decimal") from exc
    if not number.is_finite():
        _error(path, "must be finite")
    if positive and number <= 0:
        _error(path, "must be greater than zero")
    if not positive and number < 0:
        _error(path, "must not be negative")
    return number


def _https_url(value: object, path: str) -> str:
    text = _string(value, path)
    split = urlsplit(text)
    if split.scheme != "https" or not split.netloc or split.username or split.password:
        _error(path, "must be an HTTPS URL without embedded credentials")
    return text


def _validate_base(record: dict[str, object]) -> str:
    if record.get("schema_version") != 1:
        _error("schema_version", "must be 1")
    record_type = _string(record.get("record_type"), "record_type")
    if record_type not in {"restaurant_profile", "campaign_plan", "campaign_result"}:
        _error("record_type", "is unsupported")
    _id(record.get("record_id"), "record_id")
    _timestamp(record.get("updated_at"), "updated_at")
    return record_type


def _validate_profile(record: dict[str, object]) -> None:
    _strict(record, PROFILE_KEYS, "restaurant_profile")
    restaurant = _object(record["restaurant"], "restaurant")
    _strict(
        restaurant,
        {
            "name",
            "location",
            "timezone",
            "locale",
            "service_modes",
            "cuisine",
            "positioning",
            "audiences",
            "voice",
            "languages",
        },
        "restaurant",
    )
    for field in ("name", "location", "timezone", "locale", "positioning", "voice"):
        _string(restaurant[field], f"restaurant.{field}")
    for field in ("service_modes", "cuisine", "audiences", "languages"):
        _string_list(restaurant[field], f"restaurant.{field}")
    for index, surface_value in enumerate(_list(record["surfaces"], "surfaces")):
        surface = _object(surface_value, f"surfaces[{index}]")
        _strict(surface, {"name", "type", "status", "url"}, f"surfaces[{index}]")
        _string(surface["name"], f"surfaces[{index}].name")
        _string(surface["type"], f"surfaces[{index}].type")
        if surface["status"] not in {"verified", "unverified", "unavailable"}:
            _error(f"surfaces[{index}].status", "is unsupported")
        if surface["url"] is not None:
            _https_url(surface["url"], f"surfaces[{index}].url")
    _object(record["operations"], "operations")
    _object(record["measurement"], "measurement")
    _list(record["claim_sources"], "claim_sources")
    _object(record["direct_marketing"], "direct_marketing")
    _list(record["approvals"], "approvals")
    _string_list(record["unknowns"], "unknowns")


def _validate_claim(claim_value: object, index: int, publish_ready: bool) -> None:
    path = f"claims[{index}]"
    claim = _object(claim_value, path)
    _strict(claim, {"claim_id", "type", "text", "source", "status", "expires_on"}, path)
    _id(claim["claim_id"], f"{path}.claim_id")
    if claim["type"] not in CLAIM_TYPES:
        _error(f"{path}.type", "is unsupported")
    _string(claim["text"], f"{path}.text")
    if claim["status"] not in {"unknown", "draft", "verified", "rejected", "expired"}:
        _error(f"{path}.status", "is unsupported")
    if claim["source"] is not None:
        _string(claim["source"], f"{path}.source")
    if claim["expires_on"] is not None:
        _date(claim["expires_on"], f"{path}.expires_on")
    if publish_ready and claim["type"] in HIGH_RISK_CLAIMS:
        if claim["status"] != "verified" or not claim["source"]:
            _error(path, "high-risk claim must be verified with a source before publication")


def _validate_economics(value: object, required: bool) -> None:
    if value is None:
        if required:
            _error("economics", "is required for an offer campaign")
        return
    economics = _object(value, "economics")
    _strict(
        economics,
        {
            "currency",
            "baseline_price",
            "variable_cost",
            "promoted_price",
            "fixed_cost",
            "expected_attachment_contribution",
            "scenarios",
            "assumptions",
        },
        "economics",
    )
    currency = _string(economics["currency"], "economics.currency")
    if not re.fullmatch(r"[A-Z]{3}", currency):
        _error("economics.currency", "must be a three-letter uppercase currency code")
    baseline = _decimal(economics["baseline_price"], "economics.baseline_price", positive=True)
    cost = _decimal(economics["variable_cost"], "economics.variable_cost")
    promoted = _decimal(economics["promoted_price"], "economics.promoted_price", positive=True)
    _decimal(economics["fixed_cost"], "economics.fixed_cost")
    attachment = _decimal(
        economics["expected_attachment_contribution"],
        "economics.expected_attachment_contribution",
    )
    if cost >= baseline:
        _error("economics.variable_cost", "must be lower than baseline_price")
    if promoted - cost + attachment <= 0:
        _error("economics", "promoted contribution must be greater than zero")
    names: list[str] = []
    units: list[int] = []
    for index, scenario_value in enumerate(_list(economics["scenarios"], "economics.scenarios")):
        scenario = _object(scenario_value, f"economics.scenarios[{index}]")
        _strict(
            scenario,
            {"name", "incremental_units"},
            f"economics.scenarios[{index}]",
        )
        name = _string(scenario["name"], f"economics.scenarios[{index}].name")
        if isinstance(scenario["incremental_units"], bool) or not isinstance(
            scenario["incremental_units"], int
        ):
            _error(
                f"economics.scenarios[{index}].incremental_units",
                "must be an integer",
            )
        if scenario["incremental_units"] < 0:
            _error(
                f"economics.scenarios[{index}].incremental_units",
                "must not be negative",
            )
        names.append(name)
        units.append(scenario["incremental_units"])
    if names != ["conservative", "expected", "upside"]:
        _error("economics.scenarios", "must be conservative, expected, then upside")
    if units != sorted(units):
        _error("economics.scenarios", "incremental_units must be non-decreasing")
    _string_list(economics["assumptions"], "economics.assumptions")


def _validate_utm(utm_value: object, path: str) -> None:
    utm = _object(utm_value, path)
    _strict(utm, {"id", "source", "medium", "campaign", "content"}, path)
    for field, value in utm.items():
        text = _string(value, f"{path}.{field}")
        if not UTM_PATTERN.fullmatch(text):
            _error(
                f"{path}.{field}",
                "must be lowercase and contain only letters, digits, underscores, or hyphens",
            )
        if EMAIL_PATTERN.search(text) or PHONE_PATTERN.search(text):
            _error(f"{path}.{field}", "must not contain personal information")


def _validate_plan(record: dict[str, object]) -> None:
    _strict(record, PLAN_KEYS, "campaign_plan")
    campaign = _object(record["campaign"], "campaign")
    _strict(
        campaign,
        {
            "campaign_id",
            "name",
            "archetype",
            "objective",
            "status",
            "jurisdiction",
            "timezone",
            "start_date",
            "end_date",
        },
        "campaign",
    )
    _id(campaign["campaign_id"], "campaign.campaign_id")
    for field in ("name", "objective", "jurisdiction", "timezone"):
        _string(campaign[field], f"campaign.{field}")
    if campaign["archetype"] not in ARCHETYPES:
        _error("campaign.archetype", "is unsupported")
    if campaign["status"] not in PLAN_STATUSES:
        _error("campaign.status", "is unsupported")
    start = _date(campaign["start_date"], "campaign.start_date")
    end = _date(campaign["end_date"], "campaign.end_date")
    if end < start:
        _error("campaign.end_date", "must not be before start_date")
    publish_ready = campaign["status"] in {"approved", "scheduled", "live"}

    truth = _object(record["truth"], "truth")
    _strict(
        truth,
        {
            "item_name",
            "price",
            "dates_confirmed",
            "terms",
            "availability",
            "eligible_channels",
            "inventory_status",
            "capacity_status",
            "destination_url",
            "staff_brief_status",
            "blockers",
        },
        "truth",
    )
    _string(truth["item_name"], "truth.item_name")
    _decimal(truth["price"], "truth.price", positive=True)
    _boolean(truth["dates_confirmed"], "truth.dates_confirmed")
    _string(truth["terms"], "truth.terms")
    _string(truth["availability"], "truth.availability")
    _string_list(truth["eligible_channels"], "truth.eligible_channels")
    for field in ("inventory_status", "capacity_status", "staff_brief_status"):
        if truth[field] not in {"unknown", "blocked", "ready", "not_applicable"}:
            _error(f"truth.{field}", "is unsupported")
    _https_url(truth["destination_url"], "truth.destination_url")
    blockers = _string_list(truth["blockers"], "truth.blockers")
    if publish_ready:
        if blockers or record["unknowns"]:
            _error("campaign.status", "cannot be publication-ready with blockers or unknowns")
        if not truth["dates_confirmed"]:
            _error("truth.dates_confirmed", "must be true before publication")
        for field in ("inventory_status", "capacity_status", "staff_brief_status"):
            if truth[field] not in {"ready", "not_applicable"}:
                _error(f"truth.{field}", "must be ready or not_applicable before publication")

    _validate_economics(record["economics"], campaign["archetype"] == "offer")
    audience = _object(record["audience"], "audience")
    _strict(audience, {"segment", "occasion"}, "audience")
    _string(audience["segment"], "audience.segment")
    _string(audience["occasion"], "audience.occasion")
    message = _object(record["message"], "message")
    _strict(message, {"promise", "proof", "cta"}, "message")
    _string(message["promise"], "message.promise")
    _string_list(message["proof"], "message.proof")
    _string(message["cta"], "message.cta")

    claims = _list(record["claims"], "claims")
    for index, claim in enumerate(claims):
        _validate_claim(claim, index, publish_ready)
    claim_ids = [claim["claim_id"] for claim in claims if isinstance(claim, dict)]
    if len(claim_ids) != len(set(claim_ids)):
        _error("claims", "claim_id values must be unique")

    approvals = _list(record["approvals"], "approvals")
    approved_targets: set[str] = set()
    for index, approval_value in enumerate(approvals):
        path = f"approvals[{index}]"
        approval = _object(approval_value, path)
        _strict(
            approval,
            {"approval_id", "action", "target", "scope", "status", "approver", "spend_cap"},
            path,
        )
        _id(approval["approval_id"], f"{path}.approval_id")
        for field in ("action", "target", "scope"):
            _string(approval[field], f"{path}.{field}")
        if approval["status"] not in {"pending", "approved", "rejected", "expired"}:
            _error(f"{path}.status", "is unsupported")
        if approval["approver"] is not None:
            _string(approval["approver"], f"{path}.approver")
        if approval["spend_cap"] is not None:
            _decimal(approval["spend_cap"], f"{path}.spend_cap")
        if approval["status"] == "approved":
            approved_targets.add(str(approval["target"]))

    deliverables = _list(record["deliverables"], "deliverables")
    channels: set[str] = set()
    for index, deliverable_value in enumerate(deliverables):
        path = f"deliverables[{index}]"
        deliverable = _object(deliverable_value, path)
        _strict(
            deliverable,
            {
                "deliverable_id",
                "channel",
                "phase",
                "owner",
                "status",
                "destination",
                "expires_on",
            },
            path,
        )
        deliverable_id = _id(deliverable["deliverable_id"], f"{path}.deliverable_id")
        channel = _string(deliverable["channel"], f"{path}.channel")
        channels.add(channel)
        for field in ("phase", "owner", "destination"):
            _string(deliverable[field], f"{path}.{field}")
        if deliverable["status"] not in {
            "draft",
            "fact_checked",
            "approved",
            "scheduled",
            "published",
            "verified",
            "expired",
            "withdrawn",
        }:
            _error(f"{path}.status", "is unsupported")
        if deliverable["expires_on"] is not None:
            _date(deliverable["expires_on"], f"{path}.expires_on")
        if deliverable["status"] in MUTATING_DELIVERABLE_STATES:
            if deliverable_id not in approved_targets:
                _error(path, "mutating status requires an approved exact-target approval")

    measurement = _object(record["measurement"], "measurement")
    _strict(
        measurement,
        {
            "primary_kpi",
            "baseline",
            "attribution_method",
            "utm",
            "diagnostic_metrics",
            "guardrails",
        },
        "measurement",
    )
    for field in ("primary_kpi", "baseline", "attribution_method"):
        _string(measurement[field], f"measurement.{field}")
    if measurement["primary_kpi"].lower() in {
        "reach",
        "views",
        "impressions",
        "engagement",
        "likes",
    }:
        _error("measurement.primary_kpi", "must be a business outcome, not a vanity metric")
    if measurement["utm"] is not None:
        _validate_utm(measurement["utm"], "measurement.utm")
    _string_list(measurement["diagnostic_metrics"], "measurement.diagnostic_metrics")
    _string_list(measurement["guardrails"], "measurement.guardrails")

    monitoring = _object(record["monitoring"], "monitoring")
    _strict(monitoring, {"owner", "cadence", "pause_conditions"}, "monitoring")
    _string(monitoring["owner"], "monitoring.owner")
    _string(monitoring["cadence"], "monitoring.cadence")
    _string_list(monitoring["pause_conditions"], "monitoring.pause_conditions")
    expiry = _object(record["expiry"], "expiry")
    _strict(expiry, {"owner", "actions"}, "expiry")
    _string(expiry["owner"], "expiry.owner")
    _string_list(expiry["actions"], "expiry.actions")

    compliance = _object(record["compliance"], "compliance")
    _strict(
        compliance,
        {"direct_marketing", "influencer", "alcohol", "review_policy"},
        "compliance",
    )
    direct = compliance["direct_marketing"]
    if channels.intersection({"email", "sms", "push"}):
        direct_obj = _object(direct, "compliance.direct_marketing")
        _strict(
            direct_obj,
            {
                "jurisdiction",
                "consent_basis",
                "sender_identity",
                "unsubscribe_process",
                "suppression_process",
            },
            "compliance.direct_marketing",
        )
        for field in direct_obj:
            _string(direct_obj[field], f"compliance.direct_marketing.{field}")
    elif direct is not None:
        _object(direct, "compliance.direct_marketing")
    influencer = compliance["influencer"]
    if "influencer" in channels:
        influencer_obj = _object(influencer, "compliance.influencer")
        _strict(
            influencer_obj,
            {"jurisdiction", "compensation", "disclosure", "agreement_status"},
            "compliance.influencer",
        )
        for field in ("jurisdiction", "compensation", "disclosure"):
            _string(influencer_obj[field], f"compliance.influencer.{field}")
        if influencer_obj["agreement_status"] not in {"draft", "approved"}:
            _error("compliance.influencer.agreement_status", "is unsupported")
    elif influencer is not None:
        _object(influencer, "compliance.influencer")
    alcohol = compliance["alcohol"]
    if alcohol is not None:
        alcohol_obj = _object(alcohol, "compliance.alcohol")
        _strict(
            alcohol_obj,
            {
                "jurisdiction",
                "responsible_service_check",
                "rule_source",
                "approval_status",
            },
            "compliance.alcohol",
        )
        _string(alcohol_obj["jurisdiction"], "compliance.alcohol.jurisdiction")
        _boolean(
            alcohol_obj["responsible_service_check"],
            "compliance.alcohol.responsible_service_check",
        )
        _string(alcohol_obj["rule_source"], "compliance.alcohol.rule_source")
        if alcohol_obj["approval_status"] not in {"pending", "approved", "rejected"}:
            _error("compliance.alcohol.approval_status", "is unsupported")
        if publish_ready and (
            not alcohol_obj["responsible_service_check"]
            or alcohol_obj["approval_status"] != "approved"
        ):
            _error("compliance.alcohol", "must pass responsible-service and approval gates")
    review_policy = _object(compliance["review_policy"], "compliance.review_policy")
    _strict(
        review_policy,
        {
            "no_fake_reviews",
            "no_review_gating",
            "no_sentiment_incentive",
            "no_revision_removal_incentive",
        },
        "compliance.review_policy",
    )
    for field in review_policy:
        if _boolean(review_policy[field], f"compliance.review_policy.{field}") is not True:
            _error(f"compliance.review_policy.{field}", "must be true")
    _string_list(record["unknowns"], "unknowns")


def _validate_result(record: dict[str, object]) -> None:
    _strict(record, RESULT_KEYS, "campaign_result")
    _id(record["campaign_id"], "campaign_id")
    if record["status"] not in {"closed", "withdrawn"}:
        _error("status", "must be closed or withdrawn")
    _timestamp(record["closed_at"], "closed_at")
    for index, observation_value in enumerate(_list(record["observations"], "observations")):
        observation = _object(observation_value, f"observations[{index}]")
        _strict(
            observation,
            {"metric", "value", "source", "period"},
            f"observations[{index}]",
        )
        for field in observation:
            _string(observation[field], f"observations[{index}].{field}")
    for index, calculation_value in enumerate(_list(record["calculations"], "calculations")):
        calculation = _object(calculation_value, f"calculations[{index}]")
        _strict(
            calculation,
            {"name", "value", "formula", "assumptions"},
            f"calculations[{index}]",
        )
        for field in ("name", "value", "formula"):
            _string(calculation[field], f"calculations[{index}].{field}")
        _string_list(
            calculation["assumptions"],
            f"calculations[{index}].assumptions",
        )
    for index, inference_value in enumerate(_list(record["inferences"], "inferences")):
        inference = _object(inference_value, f"inferences[{index}]")
        _strict(
            inference,
            {"statement", "basis", "confidence"},
            f"inferences[{index}]",
        )
        for field in inference:
            _string(inference[field], f"inferences[{index}].{field}")
    _string_list(record["unknowns"], "unknowns")
    _string_list(record["decisions"], "decisions")
    _boolean(record["expiry_verified"], "expiry_verified")
    _string_list(record["retained_evidence"], "retained_evidence")


def validate_record(record: object) -> dict[str, object]:
    payload = _object(record, "record")
    record_type = _validate_base(payload)
    if record_type == "restaurant_profile":
        _validate_profile(payload)
    elif record_type == "campaign_plan":
        _validate_plan(payload)
    else:
        _validate_result(payload)
    return payload


def load_record(path: Path) -> dict[str, object]:
    if path.stat().st_size > MAX_RECORD_BYTES:
        _error("record", "exceeds the 2 MiB safety limit")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RecordError(f"{path}: cannot read valid UTF-8 JSON: {exc}") from exc
    return validate_record(payload)


def _money(number: Decimal) -> str:
    return str(number.quantize(Decimal("0.01")))


def economics_summary(record: dict[str, object]) -> dict[str, object]:
    if record["record_type"] != "campaign_plan":
        _error("record_type", "economics requires a campaign_plan")
    economics = record["economics"]
    if not isinstance(economics, dict):
        _error("economics", "is not available")
    baseline_price = Decimal(str(economics["baseline_price"]))
    variable_cost = Decimal(str(economics["variable_cost"]))
    promoted_price = Decimal(str(economics["promoted_price"]))
    fixed_cost = Decimal(str(economics["fixed_cost"]))
    attachment = Decimal(str(economics["expected_attachment_contribution"]))
    baseline_contribution = baseline_price - variable_cost
    promoted_contribution = promoted_price - variable_cost + attachment
    required_units = (
        Decimal("0")
        if fixed_cost == 0
        else (fixed_cost / promoted_contribution).to_integral_value(rounding=ROUND_CEILING)
    )
    scenarios = []
    for scenario in economics["scenarios"]:
        units = Decimal(str(scenario["incremental_units"]))
        scenarios.append(
            {
                "name": scenario["name"],
                "incremental_units": scenario["incremental_units"],
                "incremental_contribution_after_fixed_cost": _money(
                    units * promoted_contribution - fixed_cost
                ),
            }
        )
    return {
        "campaign_id": record["campaign"]["campaign_id"],
        "currency": economics["currency"],
        "baseline_contribution_per_unit": _money(baseline_contribution),
        "promoted_contribution_per_incremental_unit": _money(promoted_contribution),
        "contribution_change_per_unit": _money(
            promoted_contribution - baseline_contribution
        ),
        "incremental_units_to_cover_fixed_cost": int(required_units),
        "scenarios": scenarios,
        "assumptions": economics["assumptions"],
        "interpretation_boundary": (
            "This is contribution arithmetic from supplied assumptions, not proof of "
            "incremental demand, attribution, or profit."
        ),
    }


def build_utm(record: dict[str, object]) -> str:
    if record["record_type"] != "campaign_plan":
        _error("record_type", "utm requires a campaign_plan")
    destination = _https_url(record["truth"]["destination_url"], "truth.destination_url")
    utm = record["measurement"]["utm"]
    if utm is None:
        _error("measurement.utm", "is not available")
    _validate_utm(utm, "measurement.utm")
    split = urlsplit(destination)
    query = parse_qsl(split.query, keep_blank_values=True)
    query.extend(
        [
            ("utm_id", utm["id"]),
            ("utm_source", utm["source"]),
            ("utm_medium", utm["medium"]),
            ("utm_campaign", utm["campaign"]),
            ("utm_content", utm["content"]),
        ]
    )
    return urlunsplit((split.scheme, split.netloc, split.path, urlencode(query), split.fragment))


def compact_summary(record: dict[str, object]) -> dict[str, object]:
    record_type = record["record_type"]
    if record_type == "restaurant_profile":
        return {
            "record_type": record_type,
            "restaurant": record["restaurant"]["name"],
            "verified_surfaces": sum(
                surface["status"] == "verified" for surface in record["surfaces"]
            ),
            "unknowns": record["unknowns"],
        }
    if record_type == "campaign_result":
        return {
            "record_type": record_type,
            "campaign_id": record["campaign_id"],
            "status": record["status"],
            "expiry_verified": record["expiry_verified"],
            "observations": len(record["observations"]),
            "calculations": len(record["calculations"]),
            "inferences": len(record["inferences"]),
            "unknowns": record["unknowns"],
            "decisions": record["decisions"],
        }
    blockers = list(record["truth"]["blockers"]) + list(record["unknowns"])
    pending_approvals = [
        approval["approval_id"]
        for approval in record["approvals"]
        if approval["status"] == "pending"
    ]
    return {
        "record_type": record_type,
        "campaign_id": record["campaign"]["campaign_id"],
        "archetype": record["campaign"]["archetype"],
        "status": record["campaign"]["status"],
        "primary_kpi": record["measurement"]["primary_kpi"],
        "blockers": blockers,
        "pending_approvals": pending_approvals,
        "deliverables": {
            status: sum(
                deliverable["status"] == status
                for deliverable in record["deliverables"]
            )
            for status in sorted(
                {deliverable["status"] for deliverable in record["deliverables"]}
            )
        },
        "next_boundary": (
            "Resolve blockers"
            if blockers
            else "Obtain exact-target approvals before external changes"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "economics", "utm", "summary"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        record = load_record(args.record)
        if args.command == "validate":
            output: object = {
                "valid": True,
                "record_type": record["record_type"],
                "record_id": record["record_id"],
            }
        elif args.command == "economics":
            output = economics_summary(record)
        elif args.command == "utm":
            output = {"url": build_utm(record)}
        else:
            output = compact_summary(record)
        print(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False))
        return 0
    except (RecordError, OSError) as exc:
        print(f"Restaurant marketing record error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
