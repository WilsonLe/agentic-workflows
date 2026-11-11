# Reproducible backtesting and accounting

Adapted and rewritten for Agentic Workflows; see [sources and changes](upstream.md). Inputs
are a frozen candidate from [hypotheses](hypotheses.md), identified data, declared
splits, costs, baseline, and the project's existing backtest contracts.

## Inspect the existing engine first

Read its strategy interface, event ordering, data adjustments, sizing, fill/cost
models, accounting, and tests before choosing commands or extending it. Reuse the
existing engine and record its version and unsupported behavior. Do not build a
second simulator or replace missing semantics with a summary-metric calculator.
If no suitable engine exists, report the missing contract and scope that work
through the development workflow before treating a simulation as valid evidence.

Confirm that the data supports each intended observation and execution event.
Inspect gaps, duplicate/out-of-order events, stale quotes, timestamps, instrument
identity, trading calendars, point-in-time membership, and asset-specific fields.
Critical gaps leave the experiment `data_blocked`; invented bars cannot repair it.

## Trace information into fills

For representative entries, exits, and boundary cases, trace this chain:

`information available → decision → order active → execution → position/account`

Preserve event time and information availability separately. Publication delays,
bar completion, feed latency, and exchange sessions can make a recorded observation
unavailable at the proposed decision. Explain same-timestamp ordering; a blanket
one-row shift does not prove causal timing across assets or irregular observations.

Specify order activation and eligible fills for market, limit, stop, and stop-limit
orders. A signal using a completed bar cannot assume an earlier fill in that bar.
Model partial fills, cancellations, latency, rejected/unfilled orders, price limits,
halts, and participation constraints when material to the hypothesis. Treat absent
order-book or queue evidence as uncertainty, not guaranteed execution.

OHLC bars do not reveal whether a stop or target was touched first. Use adequate
finer data, a documented conservative rule, or bounds across plausible paths. Report
the affected trades and sensitivity; avoid choosing the favorable path per trade.
An intrabar trigger and fill need a consistent path, not separate favorable extrema.

## Apply costs in explicit units

Record source and effective date, instrument, currency, per-side/round-trip basis,
and units for each cost. Convert basis points, price ticks, cash per contract/share,
and percentage of notional consistently. Include commissions, exchange/regulatory
charges, spread, slippage, market impact, and applicable borrowing, financing,
funding, taxes, or roll costs. Distinguish a cost already embedded in fill prices
from one separately deducted from cash; charge it once.

Use observed or defensible base assumptions plus adverse scenarios suited to size,
liquidity, order type, and market regime. Document missing estimates. Constant
slippage can be a scenario, but a `slippage tested` flag is not execution evidence.
Do not infer capacity from volume alone or size using cash/margin not yet available.

## Reconcile the execution and account ledgers

Retain orders, fills, position changes, cash/settlement events, fees, marks, equity,
and currency conversions with stable identities and timestamps. Verify that:

- Filled quantities reconcile to position changes; exits cannot close nonexistent
  exposure and intended reversals account for both closing and opening quantities.
- Cash changes reconcile to executed consideration, income, charges, financing,
  deposits/withdrawals, and instrument-specific settlement events.
- Equity reconciles to cash, marked assets/liabilities, and unrealized amounts
  under the instrument's accounting convention; futures notional is not cash spent.
- Realized/unrealized profit, dividends/distributions, costs, and FX explain equity
  changes without double-counting variation margin or realized futures settlement.

Use actual contract prices, multipliers, expiry and settlement rules for futures
cash flows. Adjusted continuous series may support features but do not supply
tradable contract fill prices. Record both legs of a roll and their costs; a
stitching adjustment is not trading profit. Link [futures](futures.md) for details.

Include initial equity before the first trade in the equity path and drawdown
peak calculation. Declare marking cadence, missing marks, external flows, and
return conventions. Intraday drawdown and close-only drawdown answer different
questions. Resolve reconciliation discrepancies before interpreting performance.

## Produce auditable results

Save candidate and engine/code identities, immutable data identifiers or hashes,
configuration, split boundaries, seeds, invocation, and output artifact locations.
Retain failed runs and their reason. Re-running the frozen inputs should reproduce
events/accounting or disclose and bound nondeterminism.

Report gross and net results, capital/exposure assumptions, turnover, completed
position lifecycles, costs, drawdowns, and relevant risk metrics. Distinguish fills,
trades, positions, days, and independent opportunities; their counts differ.
Compare the baseline through the same execution and accounting assumptions.

Hand ledgers, reconciliation evidence, limitations, and all candidate outcomes to
[validation](validation.md). An executable or profitable backtest can still be
`validation_incomplete`; it does not establish a paper or live-trading outcome.
