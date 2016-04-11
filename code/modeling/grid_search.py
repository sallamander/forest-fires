"""A module for selecting grid search options.

This module provides a number of helper functions for 
selecting how to grid search. For the time being, it simply
holds functions for using the `sklearn.grid_search.GridSearchCV`, 
although this will be built up over time. 
"""

def get_grid_params(model_name): 
    """Return the appropriate model parameters to search over. 

    Args: 
    ----
        model_name: str
            Holds the name of the model type that will be fit, which 
            defines the parameters to search over. 

    Return: 
    ------
        param_dct: dct
    """

    if model_name == 'logit': 
        param_dct = {'penalty': ['l2'], 'C': [0.05, 0.1, 0.15]}
    elif model_name == 'random_forest': 
        param_dct = {'n_estimators': [100, 200, 400, 800, 1600], 
                'max_depth': [2, 4, 8, 16, 32]}
    elif model_name == 'gradient_boosting': 
        param_dct = {'n_estimators': [128, 256, 512, 1024], 
                'learning_rate': [0.005, 0.01, 0.05], 
                'max_depth': [2, 4, 8], 
                'max_features': [0.9, 1.0], 
                'subsample': [0.9, 1.0]}
    elif model_name == 'xgboost': 
        param_dct = {'eta': [0.005, 0.01, 0.05], 
                'num_boost_round': [128, 256, 512, 1024], 
                'max_depth': [2, 4, 8], 
                'subsample': [0.9, 1.0], 
                'colsample_bytree': [0.9, 1.0]}

    return param_dct
