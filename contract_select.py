# workflow:
#1. take into account all the contracts that are available for the day.
#2. select all the out-of-money contracts (strike at least 25% and at most 50% high or low than the underlying), that expires in 2 to 4 weeks.
#3. calculate scores for all the candidate contracts according to the scoring criteria. Set a minimum score and take at most three contracts.
#scoring criteria considers greeks, time to maturity, spread.
# at the model calibration phase, we can do a grid search that yield the best result. But at the initial moment, the criteria stays arbitrar

import pandas as pd
import os

def contract_selct(
    selct_type: str ='main',
    data : str = 'spy',
    date: str = None,
    main: pd.DataFrame = None,
    maxDTE: int = 20,
    minDTE: int = 10,
    maxDistance: int = None,
    minDistance: int = None,
    maxThata: int = None,
    minTheta: int = None,
    moneyness : str = 'out') ->pd.DataFrame:
    
"""
return a dataframe containing the information of selected contrats

input:
selct_type: "main" or "hedge", declare what type of contracts we are searching, whether the main contracts we are shorting, or the contracts that we used to hedge

date: str in form of "yyyy-mm-dd", declare the date

data : 'spy' or 'spx'

main: None when selct_type = 'main', a dataframe containing the main contract when selct_type = 'hedge'

maxDTE: max DTE
minDTE: min DTE

maxDistance: max distance
minDistance: min distance

maxThata: max Theta
minTheta: min Theta

moneyness: 'out' or 'in'
"""