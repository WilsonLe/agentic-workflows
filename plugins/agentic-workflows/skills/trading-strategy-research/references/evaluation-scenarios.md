# Evaluation scenarios

These authored maintenance walkthroughs check reachable instructions and expected
evidence boundaries. They are not recorded agent trials or market-performance
results. Read [upstream](upstream.md) for source and adaptation limits.

| Request / evidence | Required behavior and observable finish |
| --- | --- |
| “Build our finance framework using TradingAgents.” | Extend this existing research owner with a dated investment memo and the existing experiment handoff. Roles are available in one task; no runtime install, extra plugin, agents, accounts or orders follow automatically. |
| “Research this stock” with dated filings and price sources but no holdings. | Select relevant analyst lenses, link facts/calculations to source IDs, challenge the thesis and document general risk. Finish the memo without inventing portfolio exposure or allocation. A completed memo is source research, not measured strategy performance. |
| A sentiment endpoint fails while filings and market data remain available. | Mark the requested lens unavailable, explain its effect and continue independent lenses. Block only conclusions that require it; do not fabricate sentiment or silently mark it not applicable. |
| Bull and bear cite three articles repeating the same release. | Track the common origin, examine the actual release and retain material dissent/falsifiers. Three role reports are not three independent observations or a calibrated probability. |
| Risk review finds the supplied portfolio already breaches a concentration limit. | Record the dated holdings/limit and calculation. Revise, reject or defer the proposal; do not present it as satisfying the mandate or size it from debate confidence. |
| An LLM analyzes a historical date using filings retrieved today and lessons resolved afterward. | Audit source availability/version, exclude later lessons and disclose model-training/context hindsight. A dated prompt and filtered tools alone do not prove point-in-time replay. |
| A TradingAgents rating-grid report is supplied as proof of net portfolio profit. | Identify the declared recommendation-return convention and independent cells; require costed fills, positions/cash and reconciliation before a strategy/portfolio claim. Retain pending and failed cells. |
| A thesis outcome has not finished its declared horizon; later the portfolio snapshot changes. | Keep the outcome pending, preserve the frozen memo, and refresh affected portfolio/risk synthesis as a new version. Reuse unchanged source evidence only when its timing and freshness remain valid. |
| “Build a momentum strategy for stocks.” No market or dataset selected. | Establish venue/horizon/universe from context or ask for the blocking choice. Produce a falsifiable mechanism and smallest experiment; return `hypothesis_only`, with no invented backtest. |
| Historical equity universe contains only today's index members. | Identify selection/survivorship bias, preserve the available data and qualify the experiment. Obtain historical membership or label the conditional universe; block a market-wide performance claim. |
| Signal reads a completed daily close and fills at that same close. | Trace data availability and auction/order deadlines. Reject impossible sequencing; a shift alone is not proof. With sufficient intrabar/auction evidence, assess the declared mechanism rather than universally banning same-bar execution. |
| Both stop and target occur within one OHLC bar. | Record that order cannot be inferred. Use finer data or a disclosed conservative/path sensitivity; do not choose the favorable sequence. |
| A futures “winner” earns most profit at contract rollover. | Inspect actual contracts, adjustment, roll decision availability, ledger and costs. Separate signal continuity from executable cash flows; withhold the edge claim until reconciliation. |
| “Size VN30 futures like ES.” Specifications missing. | Request/source the actual venue/contract/currency/tick/multiplier and dated margin policy. Return `data_blocked` for sizing; do not substitute ES or a static vendor alias. |
| A synthetic NAV starts at 100 and immediately falls to 50. | Drawdown includes the initial NAV and records 50% depth. A running peak beginning only after the loss is an accounting failure. |
| Best Sharpe selected after 200 attempted variants; 199 failures omitted. | Restore the search history, dependent-trial assumptions and uncertainty. No generic evaluator/confidence score establishes edge. Unknown history remains a limitation. |
| A purged CV model trains on rows after a test interval. | It may be a valid research CV construction; do not label it causal walk-forward evidence. Use past-only training for chronological simulated deployment. |
| Strategy was changed after viewing the final holdout. | Retain both versions and mark that period as development/selection evidence. Seek new untouched evaluation or disclose the unresolved limitation; do not relabel it out of sample. |
| Frozen rule-based test passes its criteria and cost/regime stresses. | Link reproducible ledger/equity and uncertainty evidence; `paper_trial_candidate` may be supported. Do not force ML or open a broker connection. |
| Resume after data provider corrected history or engine configuration changed. | Compare identities, preserve old artifacts and refresh affected downstream evidence. Unchanged notes can be reused; stale performance cannot. |
| “Start trading it” follows a historical report. | Recognize a separate execution request, resolve exact account/environment/authority and the project's execution workflow. This skill does not place orders or change trading-enabled state. |

For a real maintenance check, retain the supplied request/data, instruction revision,
observed response/artifacts, deviations and limitations. Package checks establish
asset presence and portability; evaluating agent behavior or strategy performance
requires its own actual observations and authority.
