"""A module for selecting grid search options.

This module provides a number of helper functions for parameter searching. This 
holds a function for using the `sklearn.grid_search.GridSearchCV` and 
`sklearn.grid_search.RandomizedSearchCV` (a wrapper around the two). 
"""

from sklearn.grid_search import GridSearchCV, RandomizedSearchCV
import scipy.stats as scs
from preprocessing import get_target_features 
from scoring import return_scorer

def run_sklearn_param_search(model, train, cv_fold_generator, model_name, 
        random=False, num_iterations=10): 
    """Perform a model search over possible parameter values.
    
    Args: 
    ----
        model: varied
            Holds the model to perform the grid search over. Expected to implement 
            the sklearn model interface. 
        train: np.ndarray
        cv_fold_generator: SequentialTimeFold object 
            An object that generates folds to perform cross-validation over. 
        model_name: str
        random (optional): bool
            Holds whether or not to use RandomizedSearchCV or GridSearchCV. 
        num_iterations (optional): int
            Number of iterations to use for random searching (if used). 

    Returns: 
    -------
        best_model: sklearn.<searcher>.best_estimator_
        best_mean_score: float
    """

    train_target, train_features = get_target_features(train)
    eval_metric = return_scorer('auc_precision_recall')

    fit_params={}
    if random: 
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

    return best_model, best_mean_score

def _get_grid_params(model_name): 
    """Return the appropriate model parameters to search over. 

    Note: These should be scaled down heavily before actually searching.

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
        param_dct = {'n_estimators': [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024], 
                'max_depth': [2, 4, 8, 16, 32], 
                'max_features': ['sqrt', 'log2']}
    elif model_name == 'extra_trees': 
        param_dct = {'n_estimators': [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024], 
                'max_depth': [2, 4, 8, 16, 32], 
                'max_features': ['sqrt', 'log2']}
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

    Args: 
    ----
        model_name: str

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

def get_best_params(model_name): 
    """Return the model parameters to use for the final model.

    Args: 
    ----
        model_name: str

    Return: 
    ------
        best_params: dct
    """

    if model_name == 'random_forest': 
        best_params = {'n_estimators': 2, 
                'max_depth': 4}
    elif model_name == 'extra_trees': 
        best_params = {'n_estimators': 2, 
                'max_depth': 4}

    return best_params

