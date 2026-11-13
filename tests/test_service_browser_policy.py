"""Guard the single Infisical/CLI instruction owner and its distributed consumers.

These checks establish instruction/package consistency, not live agent adherence.
"""

from __future__ import annotations

from pathlib import Path
import re
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "plugins/agentic-workflows/skills"
GUIDE = SKILLS / "agentic-workflows/references/service-browser-operations.md"
INFISICAL = SKILLS / "infisical-account-operations"
SERVICES = {
    "supabase-cli": ("Supabase", "supabase", "SUPABASE_ACCESS_TOKEN"),
    "railway-account-operations": ("Railway", "railway", "RAILWAY_API_TOKEN"),
    "cloudflare-account-operations": ("Cloudflare", "cf", "CLOUDFLARE_API_TOKEN"),
    "digitalocean-account-operations": ("DigitalOcean", "doctl", "DIGITALOCEAN_ACCESS_TOKEN"),
    "vercel-account-operations": ("Vercel", "vercel", "VERCEL_TOKEN"),
}
ADDED_SERVICES = {
    "apple-app-store": ("asc", "ASC_PRIVATE_KEY"),
    "google-play": ("Fastlane", "SUPPLY_JSON_KEY_DATA"),
    "github-account-operations": ("gh", "GH_TOKEN"),
    "polar-account-operations": ("polar", "POLAR_ACCESS_TOKEN"),
    "resend-account-operations": ("resend", "RESEND_API_KEY"),
}
# Nonsecret snapshot from the requested vault inventory. This catches omission or
# accidental cross-provider routing; it establishes no current credential rights.
OBSERVED_KEYS = {
    "apple": {
        "AMSOFT_APPLE_API_KEY", "AMSOFT_APPLE_API_KEY_ID",
        "AMSOFT_APPLE_API_KEY_ISSUER_ID", "AMSOFT_APPLE_API_PROFILE",
        "AMSOFT_APPLE_HABBY_APPSTORE_CONFIG_JSON", "AMSOFT_APPLE_HABBY_APP_ID",
        "AMSOFT_APPLE_HABBY_APP_REVIEW_ACCOUNT_JSON", "AMSOFT_APPLE_HABBY_BUNDLE_ID",
        "AMSOFT_APPLE_HABBY_POSTHOG_SDK_ENV", "AMSOFT_APPLE_HABBY_POSTHOG_VALIDATION_ENV",
        "AMSOFT_APPLE_HABBY_POSTHOG_XCCONFIG", "AMSOFT_APPLE_HABBY_SIGNING_JSON",
        "AMSOFT_APPLE_HABBY_TESTFLIGHT_CONFIG_JSON", "AMSOFT_APPLE_TEAM_ID",
        "AMSOFT_APPLE_TESTFLIGHT_API_KEY", "AMSOFT_APPLE_TESTFLIGHT_API_KEY_ID",
        "AMSOFT_APPLE_TESTFLIGHT_API_KEY_ISSUER_ID", "AMSOFT_APPLE_TESTFLIGHT_API_PROFILE",
        "HABBY_APPLE_KEY_ID", "HABBY_APPLE_PRIVATE_KEY",
    },
    "github": {"VULCAN_GITHUB_TOKEN"},
    "google-play": {"GOOGLE_PLAY_ACCOUNT_CONFIG_JSON", "GOOGLE_PLAY_SERVICE_ACCOUNT_JSON"},
    "openrouter": {"OpenRouter"},
    "polar": {"HABBY_POLAR_CLI_TOKEN", "HABBY_POLAR_PRODUCTION_RUNTIME_TOKEN",
              "HABBY_POLAR_SANDBOX_ACCESS_TOKEN"},
    "resend": {"HABBY_RESEND_SENDING_API_KEY"},
    "supabase": {"AMSOFT_SUPABASE_API_KEY"},
    "vercel": {"AMSOFT_VERCEL_API_KEY"},
}
RETIRED_HELPERS = {
    "copy_openrouter_key.py", "cloudflare_api.py", "cloudflare_configure_credentials.py",
    "digitalocean_cli.py", "digitalocean_configure_credentials.py", "railway_cli.py",
    "railway_configure_credentials.py",
}


def normalized(path: Path) -> str:
    return " ".join(path.read_text().split())


class ServiceChannelPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.package = yaml.safe_load((ROOT / "catalog/plugins-v2.yaml").read_text())["packages"][0]
        cls.contract = normalized(GUIDE)

    def test_catalog_requires_service_cli_and_infisical_but_local_supabase_remains_optional(self) -> None:
        skills = {s["name"]: s for s in self.package["skills"]}
        self.assertTrue(skills["infisical-account-operations"]["prerequisites"][0]["required"])
        for name, (_, cli, token) in SERVICES.items():
            with self.subTest(skill=name):
                required = [p for p in skills[name]["prerequisites"] if p["required"]]
                access = next(p for p in skills[name]["prerequisites"] if p["name"] == "Service CLI and Infisical access")
                self.assertEqual(required, [] if name == "supabase-cli" else [access])
                self.assertIn(cli, access["setup"])
                self.assertIn(token, access["setup"])
                self.assertIn("Infisical", access["setup"])
                self.assertNotIn("Connected ", str(skills[name]["prerequisites"]))

    def test_provider_entrypoints_prompts_and_onboarding_use_same_token_owner(self) -> None:
        for name, (_, cli, token) in SERVICES.items():
            with self.subTest(skill=name):
                entry = (SKILLS / name / "SKILL.md").read_text()
                self.assertIn("infisical-account-operations/SKILL.md", entry)
                self.assertIn(f"`{cli}`", entry)
                self.assertIn(token, entry)
                prompt = yaml.safe_load((SKILLS / name / "agents/openai.yaml").read_text())["interface"]["default_prompt"]
                for phrase in ("$infisical-account-operations", cli, "tokens obtained from Infisical"):
                    self.assertIn(phrase, prompt)
                if name != "supabase-cli":
                    self.assertIn("Infisical", (SKILLS / name / "references/onboarding.md").read_text())

    def test_added_provider_skills_are_discoverable_and_use_existing_credential_owner(self) -> None:
        catalog = {s["name"]: s for s in self.package["skills"]}
        routing = (SKILLS / "agentic-workflows/SKILL.md").read_text()
        capabilities = (SKILLS.parent / "CAPABILITIES.md").read_text()
        for name, (cli, consumer) in ADDED_SERVICES.items():
            with self.subTest(skill=name):
                entry = (SKILLS / name / "SKILL.md").read_text()
                self.assertEqual(catalog[name]["harnesses"], ["codex"])
                access = next(p for p in catalog[name]["prerequisites"]
                              if p["name"] == "Service CLI and Infisical access")
                self.assertTrue(access["required"])
                self.assertIn(cli, access["setup"])
                self.assertIn(consumer, access["setup"])
                self.assertIn("infisical-account-operations/SKILL.md", entry)
                self.assertIn(f"`{name}`", routing)
                self.assertIn(f"(skills/{name}/SKILL.md)", capabilities)
                prompt = yaml.safe_load((SKILLS / name / "agents/openai.yaml").read_text())["interface"]["default_prompt"]
                self.assertIn(f"${name}", prompt)
                self.assertIn("$infisical-account-operations", prompt)
                self.assertIn("obtained from Infisical", prompt)

    def test_inventory_accounts_for_every_observed_provider_and_key(self) -> None:
        inventory_path = INFISICAL / "references/provider-inventory.md"
        inventory = inventory_path.read_text()
        apple = (SKILLS / "apple-app-store/references/credentials.md").read_text()
        self.assertEqual(sum(map(len, OBSERVED_KEYS.values())), 30)
        providers = set(re.findall(r"^\| `([a-z-]+)` \|", inventory, re.MULTILINE))
        self.assertEqual(providers, set(OBSERVED_KEYS) | {"cloudflare", "digitalocean", "posthog", "railway"})
        for provider, expected in OBSERVED_KEYS.items():
            with self.subTest(provider=provider):
                if provider == "apple":
                    found = set(re.findall(r"`((?:AMSOFT_APPLE|HABBY_APPLE)_[A-Z_]+)`", apple))
                else:
                    row = next(line for line in inventory.splitlines() if line.startswith(f"| `{provider}` |"))
                    found = set(re.findall(r"`([^`]+)`", row.split("|")[2]))
                self.assertEqual(found, expected)
        # Conditional references must be reachable from the credential owner and
        # resolve to actual files in the distributed tree, including Apple details.
        self.assertIn("references/provider-inventory.md", (INFISICAL / "SKILL.md").read_text())
        for link in re.findall(r"\]\(([^)#]+\.md)(?:#[^)]+)?\)", inventory):
            self.assertTrue((inventory_path.parent / link).is_file(), link)

    def test_channel_failure_and_secret_boundaries_are_explicit(self) -> None:
        for phrase in (
            "Use service CLIs authenticated with tokens obtained from Infisical",
            "Require a successful, nonempty result before launching the provider CLI",
            "Exclude Infisical bootstrap credentials, unrelated tokens",
            "Cached CLI login must not supply missing authentication",
            "Missing CLI support, missing/empty tokens, expiry, permission denial or target mismatch",
            "never switch to a connector",
            "Permission denial cannot be bypassed",
            "On unknown write outcome, read back before retrying",
            "Git/GitHub repository delivery retains Standard Development Workflow's existing",
            "Configuration transfer remains preferences-only",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.contract)
        for token in ("POSTHOG_CLI_API_KEY", "POSTHOG_CLI_HOST", "POSTHOG_CLI_PROJECT_ID",
                      "POLAR_ACCESS_TOKEN", "RESEND_API_KEY", "RAILWAY_TOKEN"):
            self.assertIn(token, self.contract)
        self.assertIn("select sandbox/production explicitly", self.contract)
        self.assertIn("choose exactly one appropriate type and clear the other", self.contract)

    def test_infisical_get_set_and_auth_contracts_conceal_values_and_check_outcomes(self) -> None:
        auth = normalized(INFISICAL / "references/authentication.md")
        ops = normalized(INFISICAL / "references/secret-operations.md")
        for phrase in ("system keyring", "infisical login status", "bootstrap secret cannot be retrieved",
                       "INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET", "both output streams captured",
                       "INFISICAL_TOKEN", "Do not send credentials to an inferred instance"):
            self.assertIn(phrase, auth)
        for phrase in ("--include-imports=false", "--secret-overriding=false", "--expand=false",
                       "*not found*", "single-line validation applies to provider API tokens only",
                       "create` for a new secret", "update` only when replacement is authorized",
                       "--file", "file mode 0600 and directory mode 0700", "reject symlinks",
                       "finally", "compare exact values", "Creation conflicts and update-not-found errors",
                       "shell=False", "Capture stdout/stderr before the agent tool returns",
                       "not by itself a safe provider-token bridge"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, ops)

    def test_cloudflare_resources_use_cf_without_forcing_project_migration(self) -> None:
        entry = normalized(SKILLS / "cloudflare-account-operations/SKILL.md")
        patterns = normalized(SKILLS / "cloudflare-account-operations/references/api-patterns.md")
        for phrase in ("official `cf` CLI", "cf cli search", "Wrangler-configured projects",
                       "do not run `cf migrate`", "CLOUDFLARE_API_TOKEN"):
            self.assertIn(phrase, entry)
        for phrase in ("cf zones list", "cf dns records list", "cf schema",
                       "without migration", "cannot establish authentication"):
            self.assertIn(phrase, patterns)

    def test_openrouter_runtime_uses_the_vault_without_changing_upload_authority(self) -> None:
        runtime = normalized(SKILLS / "speech-to-text/references/openrouter.md")
        for phrase in ("infisical-account-operations/SKILL.md", "/providers/openrouter",
                       "OpenRouter` key", "OPENROUTER_API_KEY", "does not authorize an audio upload or charge"):
            self.assertIn(phrase, runtime)
        self.assertIn("It does not introduce OpenRouter account-management commands", self.contract)

    def test_active_callers_do_not_reintroduce_connector_only_instructions(self) -> None:
        callers = [
            SKILLS / "agentic-workflows/SKILL.md",
            SKILLS / "agentic-workflows/references/onboarding.md",
            SKILLS / "standard-development-workflow/SKILL.md",
            SKILLS / "standard-development-workflow/references/worktree-bootstrap.md",
            SKILLS / "agentic-workflows-config-transfer/SKILL.md",
            SKILLS / "agentic-workflows-config-transfer/agents/openai.yaml",
            SKILLS / "agentic-workflows-config-transfer/references/onboarding.md",
            ROOT / "catalog/plugins-v2.yaml",
            ROOT / "README.md", ROOT / "docs/harnesses.md",
        ]
        for name in SERVICES:
            callers.extend((SKILLS / name).rglob("*.md"))
        callers.extend(SKILLS.glob("*/references/browser-selection.md"))
        stale = ("Codex connected-app contract", "Codex connected apps", "Codex owns authentication",
                 "Recover missing connections through Codex", "A missing Railway connector",
                 "provider connections remain managed by Codex",
                 "Provider connections are configured through Codex")
        for path in callers:
            text = normalized(path)
            with self.subTest(path=path.relative_to(ROOT)):
                for phrase in stale:
                    self.assertNotIn(phrase, text)
        bootstrap = normalized(SKILLS / "standard-development-workflow/references/worktree-bootstrap.md")
        self.assertIn("Exclude agent authentication stores before inventory or copy", bootstrap)
        self.assertIn("required application env/config files", bootstrap)
        self.assertIn("does not create a separate remote target", bootstrap)
        self.assertIn("without remote authentication", normalized(SKILLS / "supabase-cli/SKILL.md"))

    def test_retired_token_stores_and_custom_provider_clients_stay_retired(self) -> None:
        for name in RETIRED_HELPERS:
            self.assertFalse((ROOT / "plugins/agentic-workflows/scripts" / name).exists())
            self.assertNotIn("scripts/" + name, self.package["executables"])
        for base in (SKILLS, ROOT / "plugins/agentic-workflows/scripts"):
            for path in base.rglob("*"):
                if path.suffix not in {".md", ".py", ".yaml"}:
                    continue
                text = path.read_text()
                with self.subTest(path=path.relative_to(ROOT)):
                    self.assertNotIn(".cli/", text)
                    self.assertNotIn("project-local-cli-credentials", text)
                    for name in RETIRED_HELPERS:
                        self.assertNotIn(name, text)

    def test_every_provider_contract_link_resolves_to_single_owner(self) -> None:
        for name in (*SERVICES, *ADDED_SERVICES, "infisical-account-operations"):
            for path in (SKILLS / name).rglob("*.md"):
                for link in re.findall(r"\]\(([^)#]+service-browser-operations\.md)(?:#[^)]+)?\)", path.read_text()):
                    self.assertEqual((path.parent / link).resolve(), GUIDE.resolve())


if __name__ == "__main__":
    unittest.main()
