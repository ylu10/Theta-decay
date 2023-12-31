import pandas as pd
import os
import copy

def position_adj_cost(
    original_position: dict = None,
    adjusted_position: dict = None,
    ) ->dict:
    
    """
    return a dict containing the percentage cost/spreads for adjusting the position 
    
    input:
    original_position: last trading day position
    """
    
    main_original =  copy.deepcopy(original_position['main'])
    hedge_original = copy.deepcopy(original_position['hedge'])
    emini_original = copy.deepcopy(original_position['emini'])
    
    main_adjusted =  copy.deepcopy(adjusted_position['main'])
    hedge_adjusted = copy.deepcopy(adjusted_position['hedge'])
    emini_adjusted = copy.deepcopy(adjusted_position['emini'])
    
    # getting the notional equity of the original position
    equity_sum = 0
    for i in range(len(main_original)):
        contract_to_calc = main_original.iloc[i]
        if contract_to_calc['WEIGHT'] > 0: column = contract_to_calc.filter(regex='ASK').index
        elif contract_to_calc['WEIGHT'] <= 0: column = contract_to_calc.filter(regex='BID').index
        equity_sum = equity_sum + contract_to_calc.WEIGHT * contract_to_calc[column].values
    for i in range(len(hedge_original)):
        contract_to_calc = hedge_original.iloc[i]
        if contract_to_calc['WEIGHT'] > 0: column = contract_to_calc.filter(regex='ASK').index
        elif contract_to_calc['WEIGHT'] <= 0: column = contract_to_calc.filter(regex='BID').index
        equity_sum = equity_sum + contract_to_calc.WEIGHT * contract_to_calc[column].values
    equity_sum = equity_sum + emini_original['WEIGHT'].values * emini_original['[UNDERLYING_LAST]'].values
    # transform the weight to notional weight
    for i in range(len(main_original)):
        contract_to_adjust = main_original.iloc[i]
        if contract_to_adjust['WEIGHT'] > 0: 
            contract_to_adjust['WEIGHT'] = contract_to_adjust['WEIGHT'] * contract_to_calc.filter(regex='ASK').values / equity_sum 
        elif contract_to_adjust['WEIGHT'] <= 0: 
            contract_to_adjust['WEIGHT'] = contract_to_adjust['WEIGHT'] * contract_to_calc.filter(regex='BID').values / equity_sum
    for i in range(len(hedge_original)):
        contract_to_adjust = hedge_original.iloc[i]
        if contract_to_adjust['WEIGHT'] > 0: 
            contract_to_adjust['WEIGHT'] = contract_to_adjust['WEIGHT'] * contract_to_calc.filter(regex='ASK').values / equity_sum 
        elif contract_to_adjust['WEIGHT'] <= 0: 
            contract_to_adjust['WEIGHT'] = contract_to_adjust['WEIGHT'] * contract_to_calc.filter(regex='BID').values / equity_sum
    emini_original['WEIGHT'] = emini_original['WEIGHT'].values * emini_original['[UNDERLYING_LAST]'].values / equity_sum
    
    # getting the notional equity of the adjusted position
    equity_sum = 0
    for i in range(len(main_adjusted)):
        contract_to_calc = main_adjusted.iloc[i]
        if contract_to_calc['WEIGHT'] > 0: column = contract_to_calc.filter(regex='ASK').index
        elif contract_to_calc['WEIGHT'] <= 0: column = contract_to_calc.filter(regex='BID').index
        equity_sum = equity_sum + contract_to_calc.WEIGHT * contract_to_calc[column].values
    for i in range(len(hedge_adjusted)):
        contract_to_calc = hedge_adjusted.iloc[i]
        if contract_to_calc['WEIGHT'] > 0: column = contract_to_calc.filter(regex='ASK').index
        elif contract_to_calc['WEIGHT'] <= 0: column = contract_to_calc.filter(regex='BID').index
        equity_sum = equity_sum + contract_to_calc.WEIGHT * contract_to_calc[column].values
    equity_sum = equity_sum + emini_adjusted['WEIGHT'].values * emini_adjusted['[UNDERLYING_LAST]'].values
    # transform the weight to notional weight
    for i in range(len(main_adjusted)):
        contract_to_adjust = main_adjusted.iloc[i]
        if contract_to_adjust['WEIGHT'] > 0: 
            contract_to_adjust['WEIGHT'] = contract_to_adjust['WEIGHT'] * contract_to_calc.filter(regex='ASK').values / equity_sum 
        elif contract_to_adjust['WEIGHT'] <= 0: 
            contract_to_adjust['WEIGHT'] = contract_to_adjust['WEIGHT'] * contract_to_calc.filter(regex='BID').values / equity_sum
    for i in range(len(hedge_adjusted)):
        contract_to_adjust = hedge_adjusted.iloc[i]
        if contract_to_adjust['WEIGHT'] > 0: 
            contract_to_adjust['WEIGHT'] = contract_to_adjust['WEIGHT'] * contract_to_calc.filter(regex='ASK').values / equity_sum 
        elif contract_to_adjust['WEIGHT'] <= 0: 
            contract_to_adjust['WEIGHT'] = contract_to_adjust['WEIGHT'] * contract_to_calc.filter(regex='BID').values / equity_sum
    emini_adjusted['WEIGHT'] = emini_adjusted['WEIGHT'].values * emini_adjusted['[UNDERLYING_LAST]'].values / equity_sum
        
    #update the original main contracts according to the adjusted main contract
    #add a columns of 'adjusted weight' and set the default value to 0
    main_original['ADJUSTED WEIGHT'] = 0
    
    #concat new (if there are) contracts to the original main contract
    #set the 'adjusted weight' of the new contracts to the same value of the column 'weight'
    #set the value of the column 'weight' to 0
    k = len(main_original)
    for m in range(len(main_adjusted)):
        contract_to_update = main_adjusted.iloc[m]
        expired_date= contract_to_update.name[1]
        # print('B',m)
        # k = len(main_original)
        for n in range(k):
            # print('S',n)
            contract_to_compare = main_original.iloc[n]

            if expired_date == contract_to_compare.name[1] and contract_to_update['[STRIKE]'] == contract_to_compare['[STRIKE]']:
                main_original['ADJUSTED WEIGHT'][m] = contract_to_update['WEIGHT']
                break
            # elif (expired_date != contract_to_compare.name[1] or contract_to_update['[STRIKE]'] != contract_to_compare['[STRIKE]']): 
            else:
                if n == (k-1):
                    main_original = main_original.append(main_adjusted.iloc[[m]])
                    main_original['ADJUSTED WEIGHT'][-1] = copy.deepcopy(main_original['WEIGHT'][-1])
                    main_original['WEIGHT'][-1] = 0
                    # print('c')
            
    #update the original hedge contracts according to the adjusted hedge contract
    #add a columns of 'adjusted weight' and set the default value to 0
    hedge_original['ADJUSTED WEIGHT'] = 0
    
    #concat new (if there are) contracts to the original hedge contract
    #set the 'adjusted weight' of the new contracts to the same value of the column 'weight'
    #set the value of the column 'weight' to 0
    k = len(hedge_original)
    for m in range(len(hedge_adjusted)):
        contract_to_update = hedge_adjusted.iloc[m]
        expired_date= contract_to_update.name[1]
        # print('B',m)
        # k = len(hedge_original)
        for n in range(k):
            # print('S',n)
            contract_to_compare = hedge_original.iloc[n]

            if expired_date == contract_to_compare.name[1] and contract_to_update['[STRIKE]'] == contract_to_compare['[STRIKE]']:
                hedge_original['ADJUSTED WEIGHT'][m] = contract_to_update['WEIGHT']
                break
            # elif (expired_date != contract_to_compare.name[1] or contract_to_update['[STRIKE]'] != contract_to_compare['[STRIKE]']): 
            else:
                if n == (k-1):
                    hedge_original = hedge_original.append(hedge_adjusted.iloc[[m]])
                    hedge_original['ADJUSTED WEIGHT'][-1] = copy.deepcopy(hedge_original['WEIGHT'][-1])
                    hedge_original['WEIGHT'][-1] = 0
                    # print('c')
    
    #calculate the notional adjust cost for the main contracts
    main_original['SPREAD'] = main_original.filter(regex='ASK').values - main_original.filter(regex='BID').values
    main_original['ADJUST COST'] = 0
    k = len(main_original)
    for i in range(k):
        if main_original['WEIGHT'][i] <= 0:
            if main_original['ADJUSTED WEIGHT'][i] < main_original['WEIGHT'][i]: 
                main_original['ADJUST COST'][i] = (main_original['ADJUSTED WEIGHT'][i] - main_original['WEIGHT'][i])*main_original['SPREAD'][i]
            if main_original['ADJUSTED WEIGHT'][i] > 0:
                main_original['ADJUST COST'][i] = -main_original['ADJUSTED WEIGHT'][i] *main_original['SPREAD'][i]
        if main_original['WEIGHT'][i] > 0:
            if main_original['ADJUSTED WEIGHT'][i] > main_original['WEIGHT'][i]: 
                main_original['ADJUST COST'][i] = -(main_original['ADJUSTED WEIGHT'][i] - main_original['WEIGHT'][i])*main_original['SPREAD'][i]
            if main_original['ADJUSTED WEIGHT'][i] < 0:
                main_original['ADJUST COST'][i] = main_original['ADJUSTED WEIGHT'][i] *main_original['SPREAD'][i]

    #calculate the notional adjust cost for the hedge contracts     
    hedge_original['SPREAD'] = hedge_original.filter(regex='ASK').values - hedge_original.filter(regex='BID').values
    hedge_original['ADJUST COST'] = 0
    k = len(hedge_original)
    for i in range(k):
        if hedge_original['WEIGHT'][i] <= 0:
            if hedge_original['ADJUSTED WEIGHT'][i] < hedge_original['WEIGHT'][i]: 
                hedge_original['ADJUST COST'][i] = (hedge_original['ADJUSTED WEIGHT'][i] - hedge_original['WEIGHT'][i])*hedge_original['SPREAD'][i]
            if hedge_original['ADJUSTED WEIGHT'][i] > 0:
                hedge_original['ADJUST COST'][i] = -hedge_original['ADJUSTED WEIGHT'][i] *hedge_original['SPREAD'][i]
        if hedge_original['WEIGHT'][i] > 0:
            if hedge_original['ADJUSTED WEIGHT'][i] > hedge_original['WEIGHT'][i]: 
                hedge_original['ADJUST COST'][i] = -(hedge_original['ADJUSTED WEIGHT'][i] - hedge_original['WEIGHT'][i])*hedge_original['SPREAD'][i]
            if hedge_original['ADJUSTED WEIGHT'][i] < 0:
                hedge_original['ADJUST COST'][i] = hedge_original['ADJUSTED WEIGHT'][i] *hedge_original['SPREAD'][i]
      
    adjust_cost = (sum(main_original['ADJUST COST']) + sum(hedge_original['ADJUST COST']))/abs(equity_sum)
    
    
    return {'adjust_cost':adjust_cost, 'main':main_original, 'main_type':original_position['main_type'], 'hedge':hedge_original, 'hedge_type':original_position['hedge_type'], 'emini':emini_original}



def initial_position_cost(
    initial_position: dict = None
    ) ->dict:
    
    """
    return a dict containing the percentage cost/spreads for openning new position 
    
    input:
    initial_position: new position
    """
    
    main_initial =  copy.deepcopy(initial_position['main'])
    hedge_initial = copy.deepcopy(initial_position['hedge'])
    emini_initial = copy.deepcopy(initial_position['emini'])
    
    # getting the notional equity of the position
    equity_sum = 0
    for i in range(len(main_initial)):
        contract_to_calc = main_initial.iloc[i]
        if contract_to_calc['WEIGHT'] > 0: column = contract_to_calc.filter(regex='ASK').index
        elif contract_to_calc['WEIGHT'] <= 0: column = contract_to_calc.filter(regex='BID').index
        equity_sum = equity_sum + contract_to_calc.WEIGHT * contract_to_calc[column].values
    for i in range(len(hedge_initial)):
        contract_to_calc = hedge_initial.iloc[i]
        if contract_to_calc['WEIGHT'] > 0: column = contract_to_calc.filter(regex='ASK').index
        elif contract_to_calc['WEIGHT'] <= 0: column = contract_to_calc.filter(regex='BID').index
        equity_sum = equity_sum + contract_to_calc.WEIGHT * contract_to_calc[column].values
    equity_sum = equity_sum + emini_initial['WEIGHT'].values * emini_initial['[UNDERLYING_LAST]'].values
    
    
    #calculate the notional cost for openning the main contracts
    main_initial['SPREAD'] = main_initial.filter(regex='ASK').values - main_initial.filter(regex='BID').values
    main_initial['ADJUST COST'] = - (main_initial['SPREAD'] * abs(main_initial['WEIGHT'])).values
    
    #calculate the notional adjust cost for the hedge contracts     
    hedge_initial['SPREAD'] = hedge_initial.filter(regex='ASK').values - hedge_initial.filter(regex='BID').values
    hedge_initial['ADJUST COST'] = - (hedge_initial['SPREAD'] * abs(hedge_initial['WEIGHT'])).values

    adjust_cost = (sum(main_initial['ADJUST COST']) + sum(hedge_initial['ADJUST COST']))/abs(equity_sum)
    
    return {'adjust_cost':adjust_cost, 'main':main_initial, 'main_type':initial_position['main_type'], 'hedge':hedge_initial, 'hedge_type':initial_position['hedge_type'], 'emini':emini_initial}