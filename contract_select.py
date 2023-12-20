#workflow: A contract selection algorithm. This algorithm is used to select SPY and SPX contract that I will buy and sell. The algorithm can do contract selection according to the features (i.e. DTE, strike, theta, etc) using an utility function and defined constraints. The utility function should have penalty terms, i.e. penalty for too less or too many SPX contract.

import pandas as pd
import os

def contract_select(
    select_type: str = 'main',
    contract_type: str = 'C',
    spy_spx : str = 'spy',
    date: str = None,
    main: pd.DataFrame = None,
    minAsk: float = None,
    maxDTE: int = 30,
    minDTE: int = 0,
    maxDistance: float = None,
    minDistance: float = None,
    maxTheta: float = None,
    minTheta: float = None,
    moneyness : str = 'out',
    num: int = 3) ->pd.DataFrame:
    
    """
    return a dataframe containing the information of selected contracts
    
    input:
    select_type: "main" or "hedge", declare what type of contracts we are searching, whether the main contracts we are shorting, or the contracts that we used to hedge
    contract_type: 'C' or 'P'
    date: str in form of "yyyymmdd", declare the date
    spy_spx : 'spy' or 'spx'
    main: None when select_type = 'main', a dataframe containing the main contract when select_type = 'hedge'
    minAsk: min contract ask price
    maxDTE: max DTE
    minDTE: min DTE
    maxDistance: max distance of strike from underlying in percentage
    minDistance: min distance of strike from underlying in percentage
    maxTheta: max Theta
    minTheta: min Theta
    moneyness: 'out' or 'in'
    num: number of contract returned
    """
    
    if maxDistance == None: maxDistance = 1000
    if minDistance == None: minDistance = 0
    if maxTheta == None: maxTheta = 0
    if minTheta == None: minTheta = -100
    if minAsk == None: minAsk = 0
    
    contract_pd = pd.DataFrame()
    contract_pd =  pd.read_csv(spy_spx+'_cleaned/'+spy_spx+'_eod_'+date[:6]+'.csv', 
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
    
    contract_pd['spread_pct'] = (contract_pd['['+contract_type+'_ASK]']-contract_pd['['+contract_type+'_BID]'])*2/(contract_pd['['+contract_type+'_BID]']+contract_pd['['+contract_type+'_ASK]'])
    # Set inverted quote spread to zero
    contract_pd['spread_pct'][contract_pd['spread_pct'] < 0] = 0
    
    # filter out contract with very small ask
    contract_pd = contract_pd[contract_pd['['+contract_type+'_ASK]'] >= contract_pd['['+contract_type+'_ASK]'].mean()]
    contract_pd = contract_pd[contract_pd['['+contract_type+'_ASK]'] >= minAsk]
    
    for i in ['['+contract_type+'_DELTA]', '['+contract_type+'_GAMMA]', '['+contract_type+'_VEGA]', '['+contract_type+'_THETA]']:
        contract_pd['price_to_'+i]=(contract_pd['['+contract_type+'_BID]']+contract_pd['['+contract_type+'_ASK]'])/(2*contract_pd[i].abs())

        # utility function to select main contract    
    if select_type == 'main':    
        if spy_spx == 'spx': contract_pd['UTILITY'] = 5000*contract_pd['spread_pct'] - 0.5*contract_pd['price_to_['+contract_type+'_DELTA]'] -0.005*contract_pd['price_to_['+contract_type+'_GAMMA]'] - contract_pd['price_to_['+contract_type+'_VEGA]'] + 50* contract_pd['price_to_['+contract_type+'_THETA]']
        if spy_spx == 'spy': contract_pd['UTILITY'] = 1000*contract_pd['spread_pct'] - 3*contract_pd['price_to_['+contract_type+'_DELTA]'] -contract_pd['price_to_['+contract_type+'_GAMMA]'] - 3* contract_pd['price_to_['+contract_type+'_VEGA]'] + 50* contract_pd['price_to_['+contract_type+'_THETA]']
        
        # utility function to select hedge contract    
    if select_type == 'hedge':    
        if spy_spx == 'spx': contract_pd['UTILITY'] = 5000*contract_pd['spread_pct'] + 0.05*contract_pd['price_to_['+contract_type+'_GAMMA]'] + 15*contract_pd['price_to_['+contract_type+'_VEGA]'] - 100* contract_pd['price_to_['+contract_type+'_THETA]']
        if spy_spx == 'spy': contract_pd['UTILITY'] = 2000*contract_pd['spread_pct'] + 3*contract_pd['price_to_['+contract_type+'_GAMMA]'] + 3* contract_pd['price_to_['+contract_type+'_VEGA]'] - 100* contract_pd['price_to_['+contract_type+'_THETA]']
        
    contract_pd = contract_pd.drop(columns=['spread_pct', 'price_to_['+contract_type+'_DELTA]', 'price_to_['+contract_type+'_GAMMA]', 'price_to_['+contract_type+'_VEGA]', 'price_to_['+contract_type+'_THETA]'])

    return {select_type+'_type': spy_spx, select_type: contract_pd.sort_values(by=['UTILITY']).head(num)}
    # return contract_pd.sort_values(by=['UTILITY'])