# Futures contracts, rolls and sizing

Adapted and rewritten for Agentic Workflows; see [sources, changes and notices](upstream.md).

## Identify the actual instrument

Record exchange, product, exact contract/expiry, quote convention and currency,
contract multiplier, tick size/value, lot rules, sessions/timezone, expiry and
settlement method. Include applicable last-trade/first-notice or delivery dates,
price limits, fees and the dated exchange/broker specification sources. Initial,
maintenance and intraday margin are different requirements and may change.

Require specifications for the requested instrument. A continuous/front-month
alias alone does not identify the contract held at a historical fill. Do not
borrow ES settings for another index future, derive a micro by relabeling its
parent, or guess a VN30 contract's multiplier from an international example.
Missing specifications block sizing and executable P&L; they do not block writing
the hypothesis. A continuous series may still support a clearly limited signal
study if its construction is documented.

## Separate signals from executable P&L

Keep adjusted signal series and actual-contract prices distinct:

- Declare calendar-, volume- or open-interest-based roll selection, contract
  depth, decision time, publication delay and handling of unresolved selection.
  A roll chosen using today's final volume cannot execute earlier that day.
- Record old/new contract IDs, selection evidence available at the decision,
  old/new quotes, decision/order/fill times, quantities, costs and resulting
  positions in the roll ledger.
- Select additive, ratio, return-based or contract-level feature construction to
  match the signal's units. Additive adjustment preserves point differences,
  rather than percentage returns; ratio methods need an explicit policy for
  zero/negative prices. Back-adjusted absolute levels can change with later rolls.
- Price execution and mark-to-market from the contracts actually held. Account
  for closing/reopening, both-leg spread/fees/slippage and the specified session.
  A stitched price jump is not automatically a trading return; an adjustment
  factor is not a cash flow or an executable order price.
- For carry/curve signals, retain the relevant contract months, maturities and
  availability times. Declare tenor/annualization conventions and distinguish
  a curve proxy from realized carry after rolling and costs.

Test a roll boundary with distinct old/new prices and reconcile contracts, cash
flows and equity. Compare equivalent signal constructions where appropriate.
Raw per-contract observations are valid execution data; blindly concatenating
raw contracts is the operation that creates artificial signal/return jumps.

## Bound a proposed position

Sizing is a research estimate using a declared simulated account and risk budget.
It does not grant account access or authority to place orders. First verify that
entry/stop directions and tick units agree: an initial protective stop is below
entry for a long and above entry for a short. State a rounding policy without
altering the strategy's invalidation level to fit a budget.

For a **linear** contract, define a stressed per-contract account-currency loss:

`L = abs(entry - stop) * multiplier * FX + round_trip_costs + slippage_stress + gap_stress`

Here `FX` is account currency per unit of quote currency; all three added terms
are already in account currency per contract. State whether slippage includes
spread so it is not charged twice. Declare fees, adverse fills and gap scenarios
separately. Inverse, quanto or other nonlinear payoffs require the product's own
cash-flow model; do not apply this formula to them.

The risk-budget bound is `floor(risk_budget / L)` when inputs are valid and `L > 0`.
Then constrain integer contracts further by margin plus liquidity buffer,
available capital, liquidity/participation, position/concentration limits and
aggregate correlated exposures. Report the binding constraint. If the result is
zero or required inputs are missing, report no admissible size under the stated
assumptions; do not round up or silently increase the risk budget.

Synthetic author example: an assumed multiplier of 10 account-currency units per
point, a 4-point stop, and 15 units of combined stressed costs/gap imply `L = 55`.
A 100-unit budget permits at most one contract **before** margin and portfolio
constraints. These invented values describe no exchange contract and establish
no live loss ceiling. A stop can gap or fail to fill; margin is collateral, not
the maximum possible loss.

## Settlement, failures and evidence

Reconcile signed contract quantities, multiplier-based P&L, fees, roll cash flows,
FX conversion timing, settlement marks and equity under the engine's accounting
convention. Avoid counting daily variation margin and the same realized P&L twice.
Ensure margin breaches, limit moves, halts, expiry and unavailable roll liquidity
have an explicit simulation policy rather than impossible fills.

Report which price, contract, currency, margin and fill assumptions were verified
and which were supplied or simulated. Replay and paper fills demonstrate only
the stated environment. Broker execution, live data freshness and live trading
activation remain separate outcomes requiring their own authority and evidence.
