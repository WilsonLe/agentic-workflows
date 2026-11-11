# Strategy validation and research disposition

Adapted and rewritten for Agentic Workflows; see [sources and changes](upstream.md). Inputs
are the frozen experiment, complete trial history, identified datasets, reconciled
backtest ledgers, baseline, and documented execution/accounting limitations.
Missing critical evidence yields `validation_incomplete`, not a positive verdict.

## Audit the research path before the headline result

Check the original hypothesis and rejection criteria against what was measured.
Account for all configurations, discretionary edits, abandoned ideas, asset/date
selection, and research prompted by earlier charts or results. Unknown prior
searches limit selection-bias claims. Separate planned tests from exploratory
findings and report failures alongside successes.

Recheck availability and execution chronology, point-in-time universe membership,
adjustments, financing/borrow, futures rolls, costs, ledger reconciliation, and the
identity of the candidate actually evaluated. A source/configuration change can
invalidate earlier evidence even when the strategy name remains unchanged.

## Use splits for their stated purpose

For a chronological walk-forward claim, fit and select using only information
available before each forward evaluation period. Fit transforms, imputation,
scalers, feature selection, hyperparameters, and calibration inside training folds.
Carry the documented position/state and warm-up policy across boundaries without
training on evaluation labels or resetting away inconvenient losses.

Purge observations whose label intervals overlap an evaluation interval and apply
a justified embargo where information overlap requires it. Define these from
actual information/holding horizons. Purging and embargo do not make future-trained
folds causal. Combinatorial or other purged CV may diagnose selection or model
stability; it is not a chronological simulation of what could have been traded.

Reserve a final untouched holdout for the frozen selection procedure. Inspect it
once after rules and decision criteria are fixed. Tuning after reading its results
contaminates it; retain the result as explored evidence and obtain genuinely new
unseen data for a new confirmatory claim. Repeatedly renaming splits does not
restore an untouched test.

## Quantify uncertainty with appropriate dependence assumptions

Describe observation units, overlapping holdings/labels, cross-asset correlation,
serial dependence, outliers, and regime coverage. Raw trade count is not effective
sample size. A confidence interval based on independent trades is unsuitable when
exposures overlap or share market shocks.

Use an uncertainty method justified by the data: for example, block resampling
with defensible block length and aligned cross-asset observations. State assumptions,
resample design, seeds, and sensitivity. Ordinary independent bootstrap, Gaussian
returns, or shuffled time order can destroy dependence; do not use them silently.
Resampling one historical regime does not create evidence for unseen regimes.

Correct claims after searching many strategies or parameters using a method suited
to the search. Record all trials and their correlations. Deflated Sharpe, PBO, or
other adjustments require their own inputs and assumptions; report what they test,
units/frequency, uncertainty, and unavailable inputs. They do not give the probability
of future profit, establish causality, or replace out-of-sample execution evidence.
Do not turn a threshold or composite score into automatic deployment approval.

## Challenge the apparent edge

Compare net results with the predeclared baseline under comparable capital,
exposure, universe, calendar, and costs. Explain returns attributable to persistent
market exposure, leverage, sector/factor concentration, or a few exceptional trades.
Show economic magnitude and uncertainty, not just a significance value or win rate.

Inspect nearby parameter values and predeclared subperiod/regime results. Stress
costs, delays, missed fills, liquidity, gaps, borrow/funding, roll behavior, and
correlated portfolio losses as relevant. Keep adverse outcomes. A regime-specific
hypothesis can be valid research if regime identification is causal and its boundary
is documented; it need not win in every regime. Avoid choosing a favorable regime
after observing evaluation losses.

## Disposition and forward evidence

Use the declared criteria and retain an evidence-linked reason for the disposition:

- `rejected`: the hypothesis meets its declared rejection conditions or material
  execution/accounting evidence contradicts the proposed effect.
- `validation_incomplete`: an experiment ran but required uncertainty, robustness,
  selection, accounting, data, or forward evidence is missing or inconclusive.
- `paper_trial_candidate`: the declared historical criteria are met with stated
  limits, and a bounded paper experiment can test remaining operational assumptions.

Earlier states remain `hypothesis_only`, `data_blocked`, or `experiment_ready` when
their prerequisites have not been passed. Explain inconclusive results without
turning missing evidence into failure of the economic hypothesis itself.

Define paper-trial data/strategy versions, observation period or stopping rule,
metrics, slippage expectations, monitoring, and failure/rejection criteria before
collection. Record prospective decisions, orders, simulated fills, costs, incidents,
and deviations; do not revise earlier paper results when rules change. Paper fills
are simulated and cannot establish actual broker execution, capacity, or profitability.
Any live handoff remains a separately authorized task with unresolved risks visible.
