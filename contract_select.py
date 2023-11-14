# workflow:
#1. take into account all the contracts that are available for the day.
#2. select all the out-of-money contracts (strike at least 25% and at most 50% high or low than the underlying), that expires in 2 to 4 weeks.
#3. calculate scores for all the candidate contracts according to the scoring criteria. Set a minimum score and take at most three contracts.
#scoring criteria considers greeks, time to maturity, spread.
# at the model calibration phase, we can do a grid search that yield the best result. But at the initial moment, the criteria stays arbitrary