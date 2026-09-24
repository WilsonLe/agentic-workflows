# Offer economics

Do contribution arithmetic before recommending a discount, bundle, paid campaign, or acquisition
cost. Use current restaurant inputs and label every assumption.

`baseline contribution per unit = baseline price - variable cost`

`promoted contribution per incremental unit = promoted price - variable cost + expected attachment contribution`

`incremental units to cover fixed campaign cost = ceiling(fixed cost / promoted contribution)`

Report conservative, expected, and upside incremental-unit scenarios. For each, calculate incremental
contribution after fixed campaign cost. Also consider:

- cannibalization of full-price sales;
- redemption or platform fees;
- wastage, packaging, commissions, labor or capacity that behaves variably;
- attachment contribution supported by evidence rather than wishful averages;
- the maximum loss, spend cap, inventory cap, end date, and pause threshold.

The helper performs arithmetic from supplied assumptions; it does not establish incremental demand,
attribution, net profit, or causality. A positive scenario does not authorize launch.
