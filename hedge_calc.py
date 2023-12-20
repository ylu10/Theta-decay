#workflow
# the algorithm works like a Markwitz optimisation problem. Instead of optimising return and volatility, we optimise the greek exposure. 
# After we select the contracts we want to short and the contracts we use to hedge. The optimising goal is to maintain delta, gamma and vega neutral while keeping most of the theta. The utility function incoporates penalty terms to avoid concentration of position

from scipy.optimize import minimize, LinearConstraint, NonlinearConstraint
import pandas as pd
import numpy as np
import os

def hedge_calc(
    position: dict = None) ->dict:
    
    """
    return a dataframe containing the information of selected contrats
    
    input:
    position['main']: a dataframe containing the main contract to hedge
    position['hedge']: a dataframe containing the hedge contract to hedge
    position['emini']: dataframe containing the emini contract
    position['main_type']: type of contract, spx or spy
    position['hedge_type']: type of contract, spx or spy
    """

    if position['main_type'] == 'spy':
        columns = position['main'].filter(regex='DELTA').columns
        position['main'][columns] = position['main'][columns]/10
        # columns = position['main'].filter(regex='GAMMA').columns
        # position['main'][columns] = position['main'][columns]/10
        # columns = position['main'].filter(regex='THETA').columns
        # position['main'][columns] = position['main'][columns]*10
    if position['hedge_type'] == 'spy':
        columns = position['hedge'].filter(regex='DELTA').columns
        position['hedge'][columns] = position['hedge'][columns]/10
        # columns = position['main'].filter(regex='GAMMA').columns
        # position['hedge'][columns] = position['hedge'][columns]/10
        # columns = position['hedge'].filter(regex='THETA').columns
        # position['hedge'][columns] = position['hedge'][columns]*10
    
    # Extract columns whose names contain the desired string
    desired_string = ['GAMMA', 'VEGA', 'THETA']
    main_filtered_columns = []
    hedge_filtered_columns = []
    for i in desired_string:
        main_filtered_columns.append([col for col in position['main'].columns if i in col])
        hedge_filtered_columns.append([col for col in position['hedge'].columns if i in col])
        
    #flatten the column list
    main_filtered_columns=sum(main_filtered_columns,[])
    hedge_filtered_columns= sum(hedge_filtered_columns,[])
    
    main_mean = position['main'][main_filtered_columns].values.mean(axis=0)
    main_mean_target = main_mean.copy()
    main_mean_target[-1] = 0
    
    def fun(x):
        # x = np.array(x)
        utility = np.absolute(x.dot(position['hedge'][hedge_filtered_columns].values) - main_mean_target)
        #add weights to the residual greeks after hedging 
        utility = utility * np.array([[50],[1],[10]])
        r=np.sum(utility)
        return r
    
    def fun1(x):
        greeks = x.dot(position['hedge'][hedge_filtered_columns].values) - main_mean
        return greeks

    constraint1 = LinearConstraint(np.array(position['hedge'][hedge_filtered_columns[-1]].values), lb= main_mean[-1]*0.2, ub=[np.inf])
    constraint2 = NonlinearConstraint(lambda x: np.sum(np.absolute(x)), lb=0, ub=1, keep_feasible=True)
    constraint3 = LinearConstraint(np.array(position['hedge'][hedge_filtered_columns[0]].values), lb = main_mean_target[0] - abs(main_mean_target[0])*0.2, ub = main_mean_target[0] + abs(main_mean_target[0])*0.2)
    constraint4 = LinearConstraint(np.array(position['hedge'][hedge_filtered_columns[1]].values), keep_feasible=True, lb= main_mean_target[1] - abs(main_mean_target[1])*0.2, ub = main_mean_target[1] + abs(main_mean_target[1])*0.2)
    
    x0 = [min(0.1/len(position['hedge']),main_mean[1]/(position['hedge'][hedge_filtered_columns[1]].mean()*len(position['hedge'])))]*len(position['hedge'])
    result = minimize(fun, x0, method='trust-constr', options={'maxiter':1000}, tol=1e-6)
    position['hedge']['WEIGHT'] = result.x
    position['main']['WEIGHT'] = -1/len(position['main'])
    
    x=result.x
    
    #calculate the emini weight
    quote_date = position['main'].index[0][0]
    main_delta = sum(position['main'].filter(like='DELTA').values * position['main'].filter(like='WEIGHT').values)
    hedge_delta = sum(position['hedge'].filter(like='DELTA').values * position['hedge'].filter(like='WEIGHT').values)
    position['emini'] =  pd.read_csv('emini/emini_eod_'+ quote_date[:4]+ quote_date[5:7] +'.csv', skipinitialspace=True)
    position['emini'] = position['emini'][position['emini']['[QUOTE_DATE]'] == quote_date].set_index(['[QUOTE_DATE]'])
    position['emini']['WEIGHT'] = -main_delta-hedge_delta
    
        
    return position