# Research basis and upstream adoption

Inspected on 28 October 2026. This skill is an Agentic Workflows adaptation:
instructions were reorganized and rewritten, universal numerical gates were
removed, and stock/futures data and execution contracts were made explicit.
It does not reproduce an upstream executable, backtest engine or broker adapter.

## Pinned sources and licenses

| Source | Inspected revision | Distributed notices |
| --- | --- | --- |
| [ML4T Agent Skills](https://github.com/ml4t/skills/tree/691857537a0c8befc11dc2f2ad7a458b7c7e801c) by Stefan Jansen | `691857537a0c8befc11dc2f2ad7a458b7c7e801c` | [Apache-2.0 license](../licenses/ml4t-LICENSE.txt), [NOTICE](../licenses/ml4t-NOTICE.txt) |
| [Claude Trading Skills](https://github.com/tradermonty/claude-trading-skills/tree/c9b84196a44a56a553293114fdae1f30bdd08c58) by TraderMonty | `c9b84196a44a56a553293114fdae1f30bdd08c58` | [MIT license and copyright](../licenses/tradermonty-LICENSE.txt) |

ML4T copyright: 2026 Stefan Jansen. Its skills accompany *Machine Learning for
Algorithmic Trading*, third edition; retain the repository and book attribution
in published adaptations. Source licensing does not grant branding rights.
License/NOTICE files are preserved verbatim from the revisions above. The local
skill and references identify their adaptation; this is not an upstream endorsement.

## Adoption map

| Source paths at the pinned revision | Adopted methods | Changes and exclusions |
| --- | --- | --- |
| ML4T `workflows/strategy-workflow`, `workflows/factor-research` | Written mechanism, rejection criteria, staged research and distinct paper evidence | No mandated ML model, provider, library or deployment. Replace fixed IC/Sharpe/drawdown/duration gates with justified criteria declared in the experiment brief. |
| ML4T `concepts/point-in-time`, `lookahead-bias`, `data-leakage`, `survivorship-bias` | Availability-time joins, historical universes, fold-local learned transforms | No blanket one-day lag, universal feature shift, or assumption that all earnings arrive after the close. Eligibility follows actual information and order timing. |
| ML4T `validation/walk-forward-cv`, `purging-embargo`, `cpcv`, `deflated-sharpe`; `concepts/backtest-overfitting` | Chronological evaluation, label-overlap controls, all-trial accounting and search-aware uncertainty | Distinguish historical robustness CV from causal walk-forward simulation. Report assumptions and effective-trial uncertainty; no score proves an edge. |
| ML4T `backtest/cost-model`, `run-backtest`, `sensitivity-analysis`; `portfolio/risk-metrics`, `position-sizing` | Explicit fill/cost models, reconciled equity, perturbations and risk budgets | Do not copy numerical snippets: examples omit initial NAV in drawdown, derive alpha from Sharpe without volatility, and scale asset volatility without portfolio covariance. No new engine is bundled. |
| ML4T `data/continuous-futures` | Documented roll and adjustment methods, term structure and actual-contract identity | Distinguish adjusted signal history from raw contract fills and roll cash flows. Raw per-contract data remains necessary; continuous adjustment is not executable P&L. |
| TradeMonty `skills/trade-hypothesis-ideator`, `edge-strategy-designer`, `edge-strategy-reviewer` | Evidence-linked hypotheses, explicit rules and reviewable strategy variants | Exclude preset stock stops/reward-to-risk floors and fabricated opportunity-count heuristics. Count observed eligible events using the declared rules. |
| TradeMonty `skills/backtest-expert`, `manifoldbt-backtester` | Friction stress, sensitivity and distinction between measured metrics and supplied summaries | Aggregate-score evaluation does not execute a strategy. Do not import its Deploy/PASS labels, universal sample gates, or the long-only restricted engine bridge. |
| TradeMonty `skills/futures-position-sizer` | Contract-specific multiplier, ticks, currency and explicit direction/entry/stop | Extend sizing assumptions with costs, gaps, margin, liquidity and aggregate constraints. A stop-based estimate is not a maximum possible loss. |

Each path above identifies its `SKILL.md` and referenced material within that
repository. These methods are consolidated in this skill's focused references;
the upstream skill dependency graphs are not installed or required.

## Alternatives considered

- [QuantConnect's official Python skills](https://github.com/QuantConnect/Documentation/tree/master/skills/python)
  provide useful LEAN implementation contracts. Keep them optional when the
  project already uses LEAN; their platform assumptions do not belong in a
  general research workflow. The official [futures documentation](https://www.quantconnect.com/docs/v2/writing-algorithms/universes/futures)
  distinguishes continuous data from tradable mapped contracts.
- [Wshobson's quantitative-trading skills](https://github.com/wshobson/agents/tree/main/plugins/quantitative-trading)
  offer a concise backtesting/risk checklist. Their useful responsibilities are
  covered here without adding a second lifecycle or importing another engine.
- [Futures Edge](https://github.com/Hero988/futures-edge-skill/blob/master/SKILL.md)
  mixes strategy research, prop-firm rules, credential requests and session
  automation. No license file was identified in the inspected repository tree;
  none of its material is copied. Prop-firm rules and account setup are outside
  this skill's scope.

## Independent method references

- Bailey and López de Prado, [The Deflated Sharpe Ratio](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf):
  selection adjustment depends on the number of independent trials, sample size
  and return moments. Explain dependence and approximation limits.
- [scikit-learn TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html):
  causal ordering and a row-count gap do not automatically resolve irregular
  event times or overlapping label intervals in panels.
- CME Group, [Calculating Futures Contract Profit or Loss](https://www.cmegroup.com/education/courses/introduction-to-futures/calculating-futures-contract-profit-or-loss):
  contract size, tick size and tick value determine linear contract P&L. Verify
  current specifications for the actual exchange and instrument.

## Evidence boundary and maintenance

Research here inspected source files, dependency declarations, repository metadata
and licenses. No upstream installer, executable, paid data service or broker
connection was run. Instruction review and package checks do not establish
numerical correctness of a consuming engine, future agent adherence, empirical
strategy performance, fresh market data or execution readiness.

When updating this adaptation, pin and compare the new upstream revision, review
changed methods and licenses, then update this same source map and notices.
Revalidate any affected consuming experiment separately; an upstream status badge,
test count or package release does not refresh strategy evidence.
