"""A module for selecting grid search options.

This module provides a number of helper functions for 
selecting how to grid search. This holds functions for
using the `sklearn.grid_search.GridSearchCV` and 
`sklearn.grid_search.RandomizedSearchCV`. The two - 
`run_sklearn_grid_search` and `run_sklearn_random_search`
are effectively just wrappers around `GridSearchCV` and 
`RandomizedSearchCV`, and are the only two meant to be 
called externally. The other functions are used as helpers
to either get parameters to search over, or prep the data.
"""

from sklearn.grid_search import GridSearchCV, RandomizedSearchCV
import scipy.stats as scs
from preprocessing import get_target_features 
from supervised.gboosting import Monitor
from scoring import return_scorer

def run_sklearn_param_search(model, train, test, cv_fold_generator, 
        random=False, model_name=None): 
    """Perform a model grid search over the inputted parameters and folds. 
    
    For the given model and the relevant grid parameters, perform a 
    grid search with those grid parameters, and return the best model. 

    Args: 
    ----
        model: varied
            Holds the model to perform the grid search over. Expected 
            to implement the sklearn model interface. 
        train: np.ndarray
        test: np.ndarray
        cv_fold_generator: SequentialTimeFold/StratifiedTimeFold object 
            An object that generates folds to perform cross-validation over. 
        random: bool
            Holds whether or not to use RandomizedSearchCV or GridSearchCV. 
        model_name (optional): str
            Holds the model_name, to be used to determine if it is a 
            boosting model, and whether or not to use early stopping. Must
            be passed in if `early_stopping_tolerance` is passed in. 

    Returns: 
    -------
        best_model: sklearn.<searcher>.best_estimator_
            The best model as obtained through the parameter search. 
        best_mean_score: float
            The `mean_validation_score` from a sklearn.<searcher> object. 
        scores: list
            The scores from each run of the paramateter search. 
    """

    train_target, train_features = get_target_features(train)
    test_target, test_features = get_target_features(test)
    eval_metric = return_scorer('auc_precision_recall')
    
    fit_params = {}
    if model_name == 'gboosting' or model_name == 'xgboost': 
        # The monitor callback and xgboost use code under the hood
        # that requires these changes. 
        test_target = test_target.values.astype('float32')  
        test_features = test_features.values.astype('float32')
        test_target = test_target.copy(order='C')
        test_features = test_features.copy(order='C')

        early_stopping_tolerance = 5
        fit_params = _prep_fit_params(model_name, fit_params, 
                early_stopping_tolerance, test_features, test_target)

    if random=True: 
        params = _get_random_params(model_name)
        grid_search = RandomizedSearchCV(estimator=model, param_distributions=params, 
                scoring=eval_metric, cv=cv_fold_generator, fit_params=fit_params, 
                n_iter=num_iterations)
    else: 
        params = _get_grid_params(model_name)
        grid_search = GridSearchCV(estimator=model, param_grid=params, 
                scoring=eval_metric, cv=cv_fold_generator, fit_params=fit_params)
    grid_search.fit(train_features.values, train_target.values)

    best_model = grid_search.best_estimator_
    best_mean_score = grid_search.best_score_
    scores = grid_search.grid_scores_

    return best_model, best_mean_score, scores

def _get_grid_params(model_name): 
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
        param_dct = {'penalty': ['l1', 'l2'], 'C': [0.000001, 0.00001, 0.0001]}
    elif model_name == 'random_forest': 
        param_dct = {'n_estimators': [128, 256, 512, 1024], 
                'max_depth': [2, 4, 8, 16, 32]}
    elif model_name == 'extra_trees': 
        param_dct = {'n_estimators': [128, 256, 512, 1024], 
                'max_depth': [2, 4, 8, 16, 32]}
    elif model_name == 'gboosting': 
        param_dct = {'n_estimators': [128, 256, 512, 1024], 
                'learning_rate': [0.001, 0.01, 0.1], 
                'max_depth': [2, 4, 8], 
                'max_features': [0.5, 0.75, 1.], 
                'subsample': [0.5, 0.75, 1.]}
    elif model_name == 'xgboost': 
        param_dct = {'learning_rate': [0.001, 0.01, 0.1], 
                'n_estimators': [128, 256, 512, 1024], 
                'max_depth': [2, 4, 8], 
                'subsample': [0.5, 0.75, 1.], 
                'colsample_bytree': [0.5, 0.75, 1.]}

    return param_dct

def _get_random_params(model_name): 
    """Return some random model parameters to search over. 

    These parameters will be chosen randomly from uniform 
    distribution, allowing for use in RandomSearchCV

    Args: 
    ----
        model_name: str
            Holds the name of the model type that will be fit, 
            which defines the parameters to search over, and the 
            distributions for each. 

    Return: 
    ------
        param_dct: dct
    """

    if model_name == 'logit': 
        param_dct = {'penalty': ['l1', 'l2'], 'C': scs.uniform(0.00001, 0.0099)}
    elif model_name == 'random_forest': 
        param_dct = {'n_estimators': scs.randint(400, 1200), 
                'max_depth': scs.randint(2, 32)}
    elif model_name == 'extra_trees': 
        param_dct = {'n_estimators': scs.randint(400, 1200), 
                'max_depth': scs.randint(2, 32)}
    elif model_name == 'gboosting': 
        param_dct = {'n_estimators': scs.randint(400, 1200), 
                'learning_rate': scs.uniform(0.001, 0.099), 
                'max_depth': scs.randint(1, 8), 
                'max_features': scs.uniform(0.5, 0.5), 
                'subsample': scs.uniform(0.5, 0.5)}
    elif model_name == 'xgboost': 
        param_dct = {'learning_rate': scs.uniform(0.001, 0.099), 
                'n_estimators': scs.randint(400, 1200), 
                'max_depth': scs.randint(1, 8), 
                'subsample': scs.uniform(0.5, 0.5), 
                'colsample_bytree': scs.uniform(0.5, 0.5)}

    return param_dct

def _prep_fit_params(model_name, fit_params, 
        early_stopping_tolerance, test_features, test_target): 
    """Return the appropriate parameters to pass to a model's fit method. 

    Match the model name up with the correct parameters to pass to 
    the fit method of a model. For the time being, this only 
    applies for sklearn's GradientBoostingClassifier or xgboost. 

    Args: 
    ----
        model_name: str
        fit_params: dct
            Dictionary that holds any current parameters to pass to 
            the `fit` method of a model, to be added to. 
        early_stopping_tolerance: int
            Holds the tolerance to pass to the `supervised.gboosting.Monitor`
            object for the sklearn gradient boosting model, or to the `.fit` 
            method on an xgboost model. This tolerance controls the number 
            of training rounds that the validation error can increase/get
            worse before stopping early.

    Return:
    ------
        fit_params: dct
            Originally passed in `fit_params` dictionary with additional
            parameters added to it. 
    """

    if model_name == 'gboosting': 
        val_loss_monitor = Monitor(test_features, test_target,  
                early_stopping_tolerance)
        fit_params['monitor'] = val_loss_monitor
    elif model_name == 'xgboost': 
        fit_params['early_stopping_rounds'] = early_stopping_tolerance
        fit_params['eval_metric'] = 'logloss'
        fit_params['eval_set'] = [(test_features, test_target)]
    

    return fit_params
