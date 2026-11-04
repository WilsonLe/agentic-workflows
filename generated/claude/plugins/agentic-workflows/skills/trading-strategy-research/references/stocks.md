# Stock strategy mechanics

Method adaptation and source notices: [upstream](upstream.md).
Apply the shared [data contract](market-data.md), [execution](backtesting.md) and
[validation](validation.md) methods; this reference owns equity-specific checks.

## Historical investability

Construct the universe using membership, listing/delisting, liquidity, prices and
financial information available at each selection time. Today's index members,
successful survivors or current market-cap screen cannot reconstruct a historical
universe. Preserve identifier changes and inactive securities. If only today's
watchlist is available, label the resulting conditional-universe experiment and
its selection bias; do not claim an unbiased market-wide screen.

Match fundamentals to publication/availability and revision timestamps. Distinguish
the financial period from the release date. Verify earnings announcements and
event revisions against the actual information cut-off. Sector classifications,
analyst estimates and index changes can also be revised or published in advance.

Choose strategy families from the observed mechanism: trend/momentum, reversal,
breakout, cross-sectional relative value, event reaction or another stated thesis.
Specify why each input could be available and executable; a familiar pattern name
or an attractive chart is not evidence of positive expectancy.

## Corporate actions and execution

Declare raw, split-adjusted and dividend-adjusted series and their uses. Account
for splits in holdings and orders, dividends in cash/total return, and delisting
events and recoveries. Avoid double-counting dividends from adjusted prices plus
cash distributions. Future-adjusted price levels can distort historical absolute
price/liquidity filters; validate against point-in-time raw values as needed.

Document venue calendar/timezone, opening/closing auctions, session breaks, holidays,
price limits, halts, lot sizes, tick sizes, fees, taxes and settlement restrictions
when relevant to the strategy. Verify current rules from the venue/provider and
their historical applicability. Do not transplant US market assumptions to another
exchange. An auction signal must meet that auction's submission/data deadlines.

For short positions, establish historical borrow availability, fees/rebates,
recalls, dividend obligations and locate/short-sale restrictions. An assumed ability
to sell any ticker short is a material model limitation. If borrow history is
missing, run a clearly bounded research sensitivity or restrict the test; do not
declare the short strategy execution-ready.

## Portfolio and comparisons

Define how simultaneous candidates compete for capital, allocation, sector/issuer
concentration, gross/net exposure, turnover, leverage and participation limits.
Use a covariance-aware or conservatively bounded portfolio risk calculation when
claiming portfolio volatility; independent inverse-volatility weights alone do not
establish a portfolio target.

Compare with a suitable investable total-return benchmark and simple rules under
the same calendar, universe, capital and costs. For long/short strategies disclose
cash yield/funding, borrow costs and exposure differences. Report whether the
apparent edge is ordinary market/sector exposure, sample selection or genuinely
incremental performance within the tested assumptions. Do not call regression
residuals causal alpha without an identification design.

Finish with the historical universe and action policies, applicable restrictions,
comparison rationale, unresolved evidence and their effect on the research verdict.
