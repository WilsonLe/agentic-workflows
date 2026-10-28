# Market data and information timing

Adapted and rewritten for Agentic Workflows; see [sources, changes and notices](upstream.md).

## Establish the data contract

Use the project's existing data owner and research artifacts. Before computing a
signal, record provider/dataset, retrieval time, version or digest, coverage,
resolution, instrument identity, timezone, trading calendar, units, currency,
adjustments and known gaps. Record data-use limits. Missing paid access or private
data blocks the affected experiment; do not infer values or obtain credentials.

Distinguish these times, retaining timestamps and an explicit timezone:

| Time | Meaning and use |
| --- | --- |
| Event/observation | When the trade, bar, filing period or economic observation occurred. A period end does not establish availability. |
| Available | Earliest time the strategy could actually obtain that version of the value, including publication, vendor delay and processing. |
| Decision | When the complete input snapshot was frozen and the signal evaluated. |
| Order | Submission/cancellation time after the decision and any stated latency. |
| Fill | When an executable quote, trade or auction could satisfy the order. |

Require `available_at <= decision_at <= order_at <= fill_at` for each input and
resulting fill, with explicit tie ordering when timestamps are equal. A completed
bar's high, low and close are unavailable before completion. A date-only release
requires a documented conservative availability assumption and sensitivity check;
do not silently treat it as available at that day's open.

Retain vintages for revised macro/fundamental data. Join on availability for the
correct instrument and version; do not join on the period described or substitute
a provider's current snapshot. Prefer actual release timestamps to a universal
one-day buffer. Do not assume earnings always arrive before or after the close.

## Instrument integrity

Check duplicate/out-of-order rows, stale quotes, invalid OHLC, scale changes,
instrument identifiers and volume units against source records. Preserve missing
terminal observations as a limitation; do not silently drop failed instruments,
forward-fill indefinitely or fabricate losses.

[Stock mechanics](stocks.md) owns historical universes, corporate actions, borrow
and equity venue restrictions. [Futures mechanics](futures.md) owns contract
identity, adjustment, rolls, settlement and margin. Apply the relevant contract
before interpreting a discontinuity or selecting an execution price.

## Prevent research leakage

Compute each feature from information available at its decision. Choose lagging
from that contract: a closed bar may be used for a later order, while its close
cannot justify an earlier fill. Recompute a historical feature prefix after
appending future data; unexpected changes require investigation of adjustment,
revision or future-information dependencies.

Fit learned transformations, imputers, feature selection and hyperparameters only
inside the declared training window. Apply the fitted objects to validation/test
data. Static conversions need no artificial fit stage. Handle cross-sectional
features only after every participating instrument's inputs are available.

Build validation boundaries from timestamps and actual label intervals, rather
than assuming that five rows equal five sessions. Overlapping labels can reveal
test-period outcomes to training even with sorted rows. In panels, preserve common
time boundaries and inspect both within-instrument overlap and shared future
information across instruments. See [validation](validation.md).

## Quality failures and resume

Compare coverage with the exchange calendar and expected source cadence. A market
holiday, halt and failed fetch are different states. Do not interpolate executable
prices or convert a stale quote into an observed fill. Classify missing fields,
outliers and stale intervals; repair from authoritative data or exclude them by a
declared rule and report the resulting coverage/selection effect.

On resume, compare dataset/version, rules, availability assumptions and calendar
with the previous artifact. Reuse unchanged verified inputs. A changed source or
timing assumption invalidates dependent signals, trades and statistics; rerun
those stages and disclose any previously inspected evaluation data. Keep failure
evidence and unresolved gaps in the report instead of claiming a complete test.
