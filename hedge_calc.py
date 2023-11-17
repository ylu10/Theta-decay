#workflow
# the algorithm works like a Markwitz optimisation problem. Instead of optimising return and volatility, we optimise the greek exposure. 
# After we select the contracts we want to short and the contracts we use to hedge. The optimising goal is to maintain delta, gamma and vega neutral while keeping most of the theta. The utility function incoporates penalty terms to avoid concentration of position

import pandas as pd
import os

def hedge_calc(
    main: pd.DataFrame,
    data : str = 'spy',
    date: str = None,
    ) ->pd.DataFrame:
    
"""
return a dataframe containing the information of selected contrats

input:
main: a dataframe containing the main contract to hedge

data : 'spy' or 'spx', contract used to hedge

date: str in form of "yyyy-mm-dd", declare the date
"""