# Hypotheses and experiment design

Adapted and rewritten for Agentic Workflows; see [sources and changes](upstream.md).
This procedure produces a testable research specification, not a trading instruction.

## Inputs and scope

Use the user's objective, available market data, observations, trade records, and
the project's existing strategy contracts. Establish the market, instrument types,
direction, decision frequency, expected holding horizon, currency, and constraints.
Record unavailable inputs explicitly; do not substitute generated prices or invented
trade history for observations. Synthetic data can demonstrate mechanics only.

For each observation retain its source, observation interval, retrieval or capture
time, and availability to the original decision maker. Separate measured facts,
the user's interpretation, and the agent's proposed explanation. A chart anecdote
can motivate an experiment but cannot establish frequency, causality, or expectancy.

## Build the smallest falsifiable hypothesis

1. Describe an economic or behavioral mechanism and the competing explanation.
   Explain who supplies the proposed return and why costs or competition may erase
   it. Association alone does not identify the mechanism.
2. Define the eligible universe at each decision time, the observable signal, its
   availability delay, and the expected response horizon. Identify the inputs that
   would invalidate the hypothesis or make it untestable.
3. Propose one minimal experiment and a relevant baseline. Select a small number of
   variants justified by the mechanism; retain the reason for every added parameter.
4. Declare the primary outcome, rejection conditions, uncertainty method, risk and
   capacity constraints, and required evidence before examining evaluation results.
   Set thresholds for this question and market; no generic trade count, history
   length, win rate, Sharpe, or indicator threshold establishes viability.
5. Check feasibility against the actual data resolution, historical coverage,
   trading rules, and engine behavior. A missing critical input leaves the candidate
   `data_blocked`; a plausible explanation alone remains `hypothesis_only`.

Use the simplest baseline that answers the question: passive exposure, a fixed
rule, or another comparable strategy under the same costs, universe, and risk
budget. Decide the baseline before evaluating the candidate. Explain any mismatch.

## Specify rules without discretionary gaps

Write rules in the project's existing strategy format when one exists. State:

- Instruments, historical membership, eligibility, liquidity filters, and exclusions.
- Data fields, observation windows, adjustments, availability timestamps, calendar,
  session boundaries, time zone, and warm-up/readiness requirements.
- Exact signal calculation and decision event, including threshold equality,
  missing/stale observations, simultaneous signals, and deterministic tie-breaking.
- Entry order type, order activation time, validity, cancellation, partial fills,
  unfilled orders, and whether a position can scale or reverse.
- Exit triggers and precedence, stop/profit/time exits, gaps, session close,
  suspension, expiry, corporate actions, and futures roll behavior where relevant.
- Position sizing units, account equity basis, instrument multiplier, rounding,
  portfolio exposure, gross/net leverage, concentration, and risk limits.
- Costs, financing/borrow or funding where applicable, execution assumptions,
  mark/settlement rules, and handling of unavailable margin or borrow evidence.

Keep unresolved rule choices visible. Do not fill them with a library default or
optimistic execution assumption. Parameter values and risk limits are hypotheses
or user constraints, not established facts. A stop defines planned exit behavior;
it does not cap losses through gaps or unavailable liquidity.

## Freeze the experiment before evaluation

Bind the candidate to its rules, parameter values, universe/data snapshot, split
dates, engine/configuration version, baseline, cost scenarios, and randomness seeds
when used. Declare training, model selection, chronological evaluation, and final
holdout roles. Specify how overlapping positions and labels cross split boundaries.

Register every tried configuration, including manual threshold changes, abandoned
ideas, rejected variants, and selection prompted by charts or earlier test results.
Retain the original and create a new candidate revision for changed rules. Do not
rename a failed run into the baseline or silently narrow its evaluation interval.

If the user supplies an existing result, reconstruct its research history where
possible. Mark unknown prior trials and previously inspected periods as evidence
limits; an absent audit trail is not evidence that only one hypothesis was tried.

## Output and next decision

Update the existing research record with the mechanism, source evidence, rules,
assumptions, dependencies, baseline, frozen experiment, rejection criteria, and
trial history. Link code/data/configuration owners rather than duplicate them.

- `hypothesis_only`: an idea exists but the specification or evidence is incomplete.
- `data_blocked`: a named data or market-rule prerequisite prevents a valid test.
- `experiment_ready`: rules and prerequisites support the declared experiment.

Hand the frozen candidate to [backtesting](backtesting.md). Readiness authorizes
only the requested research step; it supplies no broker or live-trading authority.
