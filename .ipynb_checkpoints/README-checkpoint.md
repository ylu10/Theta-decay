# Theta-decay

Code design:

There should be three module to my strategy.

1. A contract selection algorithm. This algorithm is used to select SPY and SPX contract that I will buy and sell. The algorithm can do contract selection according to the features (i.e. DTE, strike, theta, etc) using an utility function and defined constraints. The utility function should have penalty terms, i.e. penalty for too less or too many SPX contract.

2. A hedge calculation algorithm. After the contract selection algorithm determines which contracts we use, the hedge calculation algorithm determines what amount of which SPX we should buy. The algorithm again uses a utility function with defined constraints that achieves delta-neutral, gamma-neutral and vega-neutral, while keeping the notional value of our hedge minimum. The utility function should also have penalty terms, i.e. penalty for concentration of position on single SPX contract.

3. A greek calculation algorithm. This algorithm tracks our position and calculate the greeks and PnL.