#workflow:
#1. after our position is taken, we record the greeks of the individual contracts and calculate the total contract.
#2. one nexttrading day, we search our contract from the dataset. Then we update the greeks of indivial contract. And then we calculate the total greeks of our position.
#3. we repeat step 2 after we adjust our position.
#4. We also record the pnl similarly as step 1 2 and 3.

import pandas as pd
import os

def greek_calc(
    position: pd.DataFrame = None,
    ) ->pd.DataFrame:
    
"""
return a dataframe containing the current greeks exposure

input:
position: current position
"""


def pnl_calc(
    position: pd.DataFrame = None,
    ) ->pd.DataFrame:
    
"""
return a dataframe containing the pnl comparing to last trading day

input:
position: current position
"""
