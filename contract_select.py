#workflow: A contract selection algorithm. This algorithm is used to select SPY and SPX contract that I will buy and sell. The algorithm can do contract selection according to the features (i.e. DTE, strike, theta, etc) using an utility function and defined constraints. The utility function should have penalty terms, i.e. penalty for too less or too many SPX contract.

import pandas as pd
import os

def contract_selct(
    selct_type: str = 'main',
    contract_type: str = 'C',
    data : str = 'spy',
    date: str = None,
    main: pd.DataFrame = None,
    maxDTE: int = 20,
    minDTE: int = 10,
    maxDistance: float = None,
    minDistance: float = None,
    maxTheta: float = None,
    minTheta: float = None,
    moneyness : str = 'out') ->pd.DataFrame:
    
"""
return a dataframe containing the information of selected contracts

input:
selct_type: "main" or "hedge", declare what type of contracts we are searching, whether the main contracts we are shorting, or the contracts that we used to hedge
contract_type: 'C' or 'P'
date: str in form of "yyyymmdd", declare the date
data : 'spy' or 'spx'
main: None when selct_type = 'main', a dataframe containing the main contract when selct_type = 'hedge'
maxDTE: max DTE
minDTE: min DTE
maxDistance: max distance of strike from underlying in percentage, can be 'None'
minDistance: min distance of strike from underlying in percentage, can be 'None'
maxTheta: max Theta, can be 'None'
minTheta: min Theta, can be 'None'
moneyness: 'out' or 'in'
"""
    if maxDistance == None: maxDistance = 1000
    if minDistance == None: minDistance = 0
    if maxTheta == None: maxTheta = 0
    if minTheta == None: minTheta = -100
    
    contract_pd = pd.DataFrame()
    
    if selct_type == 'main':
        contract_pd =  pd.read_csv(data+'_cleaned/'+data+'_eod_'+date[:6]+'.csv', 
                           index_col=['[QUOTE_DATE]','[EXPIRE_DATE]'], skipinitialspace=True)
        contract_pd = contract_pd.drop(columns='Unnamed: 0')
        contract_pd = contract_pd.iloc[contract_pd.index.get_level_values('[QUOTE_DATE]')==date[:4]+'-'+date[4:6]+'-'+date[6:]]
        contract_pd = contract_pd.loc[(contract_pd['[DTE]']>=minDTE) & (contract_pd['[DTE]']<=maxDTE) 
                & (contract_pd['[STRIKE_DISTANCE_PCT]']>=minDistance) & (contract_pd['[STRIKE_DISTANCE_PCT]']<=maxDistance)]
        if contract_type == 'C':
            contract_pd = contract_pd.drop(columns=['[P_BID]', '[P_ASK]', '[P_DELTA]', '[P_GAMMA]', '[P_VEGA]', '[P_THETA]'])
            if moneyness == 'out':
                contract_pd = contract_pd.loc[contract_pd['[STRIKE]'] >= contract_pd['[UNDERLYING_LAST]']]
                contract_pd = contract_pd.loc[(contract_pd['[C_THETA]'] >= minTheta) & (contract_pd['[C_THETA]'] <= maxTheta)]
            if moneyness == 'in':
                contract_pd = contract_pd.loc[contract_pd['[STRIKE]'] <= contract_pd['[UNDERLYING_LAST]']]
                contract_pd = contract_pd.loc[(contract_pd['[C_THETA]'] >= minTheta) & (contract_pd['[C_THETA]'] <= maxTheta)]
        if contract_type == 'P':
            contract_pd = contract_pd.drop(columns=['[C_BID]', '[C_ASK]', '[C_DELTA]', '[C_GAMMA]', '[C_VEGA]', '[C_THETA]'])
            if moneyness == 'out':
                contract_pd = contract_pd.loc[contract_pd['[STRIKE]'] <= contract_pd['[UNDERLYING_LAST]']]
                contract_pd = contract_pd.loc[(contract_pd['[P_THETA]'] >= minTheta) & (contract_pd['[P_THETA]'] <= maxTheta)]
            if moneyness == 'in':
                contract_pd = contract_pd.loc[contract_pd['[STRIKE]'] >= contract_pd['[UNDERLYING_LAST]']]
                contract_pd = contract_pd.loc[(contract_pd['[P_THETA]'] >= minTheta) & (contract_pd['[P_THETA]'] <= maxTheta)]
    
        return contract_pd