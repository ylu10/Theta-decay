#workflow
# the algorithm works like a Markwitz optimisation problem. Instead of optimising return and volatility, we optimise the greek exposure. 
# After we select the contracts we want to short and the contracts we use to hedge. The optimising goal is to maintain delta, gamma and vega neutral while keeping most of the theta. The utility function incoporates penalty terms to avoid concentration of position

from scipy.optimize import minimize, LinearConstraint, NonlinearConstraint
import pandas as pd
import numpy as np
import os

def hedge_calc(
    main: pd.DataFrame = None,
    hedge: pd.DataFrame = None,
    main_data: str = None,
    hedge_data: str = None
    ) ->pd.DataFrame:
    
    """
    return a dataframe containing the information of selected contrats
    
    input:
    main: a dataframe containing the main contract to hedge
    hedge: a dataframe containing the hedge contract to hedge
    main_data: type of contract, spx or spy
    hedge_data: type of contract, spx or spy
    """

    if main_data == 'spy':
        columns = main.filter(regex='DELTA').columns
        main[columns] = main[columns]/10
        # columns = main.filter(regex='GAMMA').columns
        # main[columns] = main[columns]/10
        # columns = main.filter(regex='THETA').columns
        # main[columns] = main[columns]*10
    if hedge_data == 'spy':
        columns = hedge.filter(regex='DELTA').columns
        hedge[columns] = hedge[columns]/10
        # columns = main.filter(regex='GAMMA').columns
        # hedge[columns] = hedge[columns]/10
        # columns = hedge.filter(regex='THETA').columns
        # hedge[columns] = hedge[columns]*10
    
    # Extract columns whose names contain the desired string
    desired_string = ['GAMMA', 'VEGA', 'THETA']
    main_filtered_columns = []
    hedge_filtered_columns = []
    for i in desired_string:
        main_filtered_columns.append([col for col in main.columns if i in col])
        hedge_filtered_columns.append([col for col in hedge.columns if i in col])
        
    #flatten the column list
    main_filtered_columns=sum(main_filtered_columns,[])
    hedge_filtered_columns= sum(hedge_filtered_columns,[])
    
    main_mean = main[main_filtered_columns].values.mean(axis=0)
    main_mean_target = main_mean.copy()
    main_mean_target[-1] = 0
    
    def fun(x):
        # x = np.array(x)
        utility = np.absolute(x.dot(hedge[hedge_filtered_columns].values) - main_mean_target)
        #add weights to the residual greeks after hedging 
        utility = utility * np.array([[50],[1],[10]])
        r=np.sum(utility)
        return r
    
    def fun1(x):
        greeks = x.dot(hedge[hedge_filtered_columns].values) - main_mean
        return greeks

    constraint1 = LinearConstraint(np.array(hedge[hedge_filtered_columns[-1]].values), lb= main_mean[-1]*0.2, ub=[np.inf])
    constraint2 = NonlinearConstraint(lambda x: np.sum(np.absolute(x)), lb=0, ub=1, keep_feasible=True)
    constraint3 = LinearConstraint(np.array(hedge[hedge_filtered_columns[0]].values), lb = main_mean_target[0] - abs(main_mean_target[0])*0.2, ub = main_mean_target[0] + abs(main_mean_target[0])*0.2)
    constraint4 = LinearConstraint(np.array(hedge[hedge_filtered_columns[1]].values), keep_feasible=True, lb= main_mean_target[1] - abs(main_mean_target[1])*0.2, ub = main_mean_target[1] + abs(main_mean_target[1])*0.2)
    
    x0 = [min(0.1/len(hedge),main_mean[1]/(hedge[hedge_filtered_columns[1]].mean()*len(hedge)))]*len(hedge)
    result = minimize(fun, x0, method='trust-constr', options={'maxiter':1000}, tol=1e-6)
    hedge['WEIGHT'] = result.x
    main['WEIGHT'] = -1/len(main)
    
    x=result.x
    
    #calculate the emini weight
    quote_date = main.index[0][0]
    main_delta = sum(main.filter(like='DELTA').values * main.filter(like='WEIGHT').values)
    hedge_delta = sum(hedge.filter(like='DELTA').values * hedge.filter(like='WEIGHT').values)
    emini =  pd.read_csv('emini/emini_eod_'+ quote_date[:4]+ quote_date[5:7] +'.csv', skipinitialspace=True)
    emini = emini[emini['[QUOTE_DATE]'] == quote_date].set_index(['[QUOTE_DATE]'])
    emini['WEIGHT'] = -main_delta-hedge_delta
    
    result = {'main':main, 'main_type':main_data, 'hedge': hedge, 'hedge_type':hedge_data, 'emini':emini}
    
    return result