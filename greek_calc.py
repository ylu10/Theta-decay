#workflow:
#1. after our position is taken, we record the greeks of the individual contracts and calculate the total contract.
#2. one nexttrading day, we search our contract from the dataset. Then we update the greeks of indivial contract. And then we calculate the total greeks of our position.
#3. we repeat step 2 after we adjust our position.
#4. We also record the pnl similarly as step 1 2 and 3.

import pandas as pd
import numpy as np
import os

def greek_calc(
    position: dict = None,
    ) ->pd.DataFrame:
    
    """
    return a dict containing the current greeks exposure
    
    input:
    position: current position
    """
    # Extract columns whose names contain the desired string
    desired_string = ['DELTA', 'GAMMA', 'VEGA', 'THETA', 'WEIGHT']
    main_filtered_columns = []
    hedge_filtered_columns = []
    for i in desired_string:
        main_filtered_columns.append([col for col in position['main'].columns if i in col])
        hedge_filtered_columns.append([col for col in position['hedge'].columns if i in col])
    #flatten the column list
    main_filtered_columns=sum(main_filtered_columns,[])
    hedge_filtered_columns= sum(hedge_filtered_columns,[])
    
    greek = np.array([i*j for (i,j) in zip(position['main'][main_filtered_columns]['WEIGHT'].values, position['main'][main_filtered_columns].drop(columns=['WEIGHT']).values)])+\
            np.array([i*j for (i,j) in zip(position['hedge'][hedge_filtered_columns]['WEIGHT'].values, position['hedge'][hedge_filtered_columns].drop(columns=['WEIGHT']).values)])
    greek = greek.sum(axis=0).reshape((1, 4))
    greek = pd.DataFrame(greek, columns=['DELTA', 'GAMMA', 'VEGA', 'THETA'])
    greek['DELTA'] = greek['DELTA'].values + position['emini']['WEIGHT'].values*1
    greek['[QUOTE_DATE]'] = position['main'].index[0][0]
    greek.set_index('[QUOTE_DATE]', inplace=True)
    
    return greek
    
def pnl_daily_calc(
    position: dict = None,
    ) ->dict:
    
    """
    return a dict containing the pnl comparing to last trading day
    
    input:
    position: last trading day position
    """
    main_pnl =  position['main'].copy()
    hedge_pnl = position['hedge'].copy()
    emini_pnl = position['emini'].copy()
    
    # getting the notional equity of the position
    equity_sum = 0
    for i in range(len(main_pnl)):
        contract_to_calc = main_pnl.iloc[i]
        if contract_to_calc['WEIGHT'] > 0: column = contract_to_calc.filter(regex='BID').index
        elif contract_to_calc['WEIGHT'] <= 0: column = contract_to_calc.filter(regex='ASK').index
        equity_sum = equity_sum + contract_to_calc.WEIGHT * contract_to_calc[column].values
    for i in range(len(hedge_pnl)):
        contract_to_calc = hedge_pnl.iloc[i]
        if contract_to_calc['WEIGHT'] > 0: column = contract_to_calc.filter(regex='BID').index
        elif contract_to_calc['WEIGHT'] <= 0: column = contract_to_calc.filter(regex='ASK').index
        equity_sum = equity_sum + contract_to_calc.WEIGHT * contract_to_calc[column].values
    equity_sum = equity_sum + emini_pnl['WEIGHT'].values * emini_pnl['[UNDERLYING_LAST]'].values
    
    # getting the next trading day's quote date and read the data
    contract_pd = pd.DataFrame()
    contract_pd =  pd.read_csv(position['main_type']+'_cleaned/'+position['main_type']+'_eod_'+main_pnl.index[0][0][:4]+main_pnl.index[0][0][5:7]+'.csv', 
                       index_col=['[QUOTE_DATE]','[EXPIRE_DATE]'], skipinitialspace=True)
    quote_date = contract_pd.index
    date_list = quote_date._levels[0]
    yesterday = main_pnl.index[0][0]
    size = len(date_list)
    loc = date_list.get_loc(yesterday)
    if loc < size -1: 
        loc = loc + 1
        date = date_list[loc]
    elif loc == size-1:
        if int(main_pnl.index[0][0][5:7]) < 12: 
            month = str(int(main_pnl.index[0][0][5:7])+1)
            contract_pd =  pd.read_csv(position['main_type']+'_cleaned/'+position['main_type']+'_eod_'+main_pnl.index[0][0][:4]+month+'.csv', 
                           index_col=['[QUOTE_DATE]','[EXPIRE_DATE]'], skipinitialspace=True)
            date = contract_pd.index._levels[0][0]
        elif int(main_pnl.index[0][0][5:7]) == 12:
            year = str(int(main_pnl.index[0][0][:4])+1)
            contract_pd =  pd.read_csv(position['main_type']+'_cleaned/'+position['main_type']+'_eod_'+year+'01'+'.csv', 
                           index_col=['[QUOTE_DATE]','[EXPIRE_DATE]'], skipinitialspace=True)
            date = contract_pd.index._levels[0][0]
    
    #getting the data for the next trading day
    contract_pd = contract_pd[contract_pd.index.get_level_values('[QUOTE_DATE]') == date]
    #dropping the unneeded columns
    contract_pd = contract_pd[main_pnl.columns[:11]]
    
    #update the main contracts to the next trading day
    filtered_data_holder = pd.DataFrame()
    for i in range(len(main_pnl)):
        contract_to_update = main_pnl.iloc[i]
        expired_date= contract_to_update.name[1]
        temp = contract_pd.loc[(date, expired_date)]
        temp=temp[temp['[STRIKE]'] == contract_to_update['[STRIKE]']]
        filtered_data_holder = filtered_data_holder.append(temp)
    
    #calculate the price difference and PNL percentage of the main contracts
    filtered_data_holder['WEIGHT'] = main_pnl['WEIGHT'].values
    filtered_data_holder['PNL'] = 0
    filtered_data_holder['PNL_PERCENTAGE'] = 0
    for i in range(len(main_pnl)):
        if main_pnl.iloc[i]['WEIGHT'] > 0: column = main_pnl.filter(regex='BID').columns
        elif main_pnl.iloc[i]['WEIGHT'] <= 0: column = main_pnl.filter(regex='ASK').columns
        filtered_data_holder['PNL'][i] = filtered_data_holder[column].iloc[i] - main_pnl[column].iloc[i]
        filtered_data_holder['PNL_PERCENTAGE'][i] = filtered_data_holder['PNL'][i] * filtered_data_holder['WEIGHT'][i] / abs(equity_sum)
    main_pnl = filtered_data_holder.copy()
    
    #calculate the price difference and PNL percentage of the hedge contracts
    contract_pd =  pd.read_csv(position['hedge_type']+'_cleaned/'+position['hedge_type']+'_eod_'+date[:4]+date[5:7]+'.csv', 
                           index_col=['[QUOTE_DATE]','[EXPIRE_DATE]'], skipinitialspace=True)
    filtered_data_holder = pd.DataFrame()
    if date in contract_pd.index.get_level_values('[QUOTE_DATE]'):
        #getting the data for the next trading day
        contract_pd = contract_pd[contract_pd.index.get_level_values('[QUOTE_DATE]') == date]
        #dropping the unneeded columns
        contract_pd = contract_pd[hedge_pnl.columns[:11]]
        for i in range(len(hedge_pnl)):
            contract_to_update = hedge_pnl.iloc[i]
            expired_date= contract_to_update.name[1]
            temp = contract_pd.loc[(date, expired_date)]
            temp=temp[temp['[STRIKE]'] == contract_to_update['[STRIKE]']]
            filtered_data_holder = filtered_data_holder.append(temp)
        #calculate the price difference of the main contracts
        filtered_data_holder['WEIGHT'] = hedge_pnl['WEIGHT'].values
        filtered_data_holder['PNL'] = 0
        filtered_data_holder['PNL_PERCENTAGE'] = 0
        for i in range(len(hedge_pnl)):
            if hedge_pnl.iloc[i]['WEIGHT'] > 0: column = hedge_pnl.filter(regex='BID').columns
            elif hedge_pnl.iloc[i]['WEIGHT'] <= 0: column = hedge_pnl.filter(regex='ASK').columns
            filtered_data_holder['PNL'][i] = filtered_data_holder[column].iloc[i] - hedge_pnl[column].iloc[i]
            filtered_data_holder['PNL_PERCENTAGE'][i] = filtered_data_holder['PNL'][i] * filtered_data_holder['WEIGHT'][i] / abs(equity_sum)
        hedge_pnl = filtered_data_holder.copy()
    elif date not in contract_pd.index.get_level_values('[QUOTE_DATE]'):
        hedge_pnl['PNL'] = 0
    
    #calculate the price difference of the emini contracts
    filtered_data_holder =  pd.read_csv('emini/emini_eod_'+ date[:4]+ date[5:7] +'.csv', skipinitialspace=True)

    if date in filtered_data_holder['[QUOTE_DATE]'].to_list():
        filtered_data_holder = filtered_data_holder[filtered_data_holder['[QUOTE_DATE]'] == date].set_index(['[QUOTE_DATE]'])
        filtered_data_holder['WEIGHT'] = emini_pnl['WEIGHT'].values
        # filtered_data_holder['PNL'] = 0
        # filtered_data_holder['PNL_PERCENTAGE'] = 0
        filtered_data_holder['PNL'] = filtered_data_holder['[UNDERLYING_LAST]'].values - emini_pnl['[UNDERLYING_LAST]'].values
        filtered_data_holder['PNL_PERCENTAGE'] = filtered_data_holder['PNL'].values * filtered_data_holder['WEIGHT'].values / abs(equity_sum)
        emini_pnl = filtered_data_holder.copy()
    elif date not in filtered_data_holder['[QUOTE_DATE]'].to_list():
        emini_pnl['PNL'] = 0
        emini_pnl['PNL_PERCENTAGE'] = 0
    
    return_sum = sum(main_pnl['PNL_PERCENTAGE']) + sum(hedge_pnl['PNL_PERCENTAGE']) + sum(emini_pnl['PNL_PERCENTAGE'])
    
    return {'daily_rtn':return_sum, 'main':main_pnl, 'main_type':position['main_type'], 'hedge':hedge_pnl, 'hedge_type':position['hedge_type'], 'emini':emini_pnl}
    # return emini_pnl