"""A module for selecting grid search options.

This module provides a number of helper functions for 
selecting how to grid search. For the time being, it simply
holds functions for using the `sklearn.grid_search.GridSearchCV`, 
although this will be built up over time. 
"""

from preprocessing import get_target_features 
from supervised.gboosting import Monitor
from scoring import return_scorer

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
    elif model_name == 'extra_trees': 
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

def sklearn_grid_search(model, params, train, test, cv_fold_generator, 
        early_stopping_tolerance=None, model_name=None): 
    """Perform a model grid search over the inputted parameters and folds. 
    
    For the given model and the relevant grid parameters, perform a 
    grid search with those grid parameters, and return the best model. 

    Args: 
    ----
        model: varied
            Holds the model to perform the grid search over. Expected 
            to implement the sklearn model interface. 
        params: dct
        train: np.ndarray
        test: np.ndarray
        cv_fold_generator: SequentialTimeFold/StratifiedTimeFold object 
            An object that generates folds to perform cross-validation over. 
        early_stopping_tolerance (optional): int
            Holds the tolerance to pass to the `supervised.gboosting.Monitor`
            object for the sklearn gradient boosting model, or to the `.fit` 
            method on an xgboost model. This tolerance controls the number 
            of training rounds that the validation error can increase/get
            worse before stopping early.
        model_name (optional): str
            Holds the model_name, to be used to determine if it is a 
            boosting model, and whether or not to use early stopping. Must
            be passed in if `early_stopping_tolerance` is passed in. 

    Returns: 
    -------
        best_model: GridSearchCV.best_estimator_
            The best model as obtained through the grid search. 
        best_mean_score: float
            The `mean_validation_score` from a GridSearchCV object. 
    """

    train_target, train_features = get_target_features(train)
    test_target, test_features = get_target_features(test)

    eval_metric = return_scorer('auc_precision_recall')
    grid_search = GridSearchCV(estimator=model, param_grid=params, 
            scoring=eval_metric, cv=cv_fold_generator)
    
    # If this was passed in, a gradient boosting model is being fitted, 
    # and early stopping should be used. 
    if early_stopping_tolerance: 
        # Sklearn allows early stopping through the passing of something 
        # to the `monitor` parameter. 
        if model_name == 'sklearn': 
            val_loss_monitor = Monitor(test_features, test_target, 
                    early_stopping_tolerance)
            grid_search.fit(train_features, train_target, 
                    monitor = val_loss_monitor)
        # XGboost for the win. It has early stopping built in. 
        elif model_name == 'xgboost': 
            grid_search.fit(train_features, train_target, 
                (test_features, test_target), eval_metric=eval_metric,
                early_stopping_rounds = early_stopping_tolerance)
        else: 
            raise Exception('Must pass in model name to use early stopping.')
    else: 
        grid_search.fit(features, target)

    return grid_search.best_estimator_, grid_search.grid_scores_[0][1]
