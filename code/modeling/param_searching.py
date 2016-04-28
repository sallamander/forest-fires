"""A module for selecting grid search options.

This module provides a number of helper functions for 
selecting how to grid search. This holds a function for
using the `sklearn.grid_search.GridSearchCV` and 
`sklearn.grid_search.RandomizedSearchCV` (a wrapper around 
the two), as well as a custom function for performing 
parameter searching over a Keras model using cross-validation. 
"""

from sklearn.grid_search import GridSearchCV, RandomizedSearchCV
import scipy.stats as scs
from preprocessing import get_target_features 
from supervised.gboosting import Monitor
from scoring import return_scorer

def run_sklearn_param_search(model, train, cv_fold_generator, 
        random=False, num_iterations=10, model_name=None, test=None): 
    """Perform a model grid search over the inputted parameters and folds. 
    
    For the given model and the relevant grid parameters, perform a 
    grid search with those grid parameters, and return the best model. 

    Args: 
    ----
        model: varied
            Holds the model to perform the grid search over. Expected 
            to implement the sklearn model interface. 
        train: np.ndarray
        cv_fold_generator: SequentialTimeFold/StratifiedTimeFold object 
            An object that generates folds to perform cross-validation over. 
        random (optional): bool
            Holds whether or not to use RandomizedSearchCV or GridSearchCV. 
        num_iterations (optional): int
            Number of iterations to use for random searching (if used). 
        model_name (optional): str
            Holds the model_name, to be used to determine if it is a 
            boosting model, and whether or not to use early stopping. Must
            be passed in if `early_stopping_tolerance` is passed in. 
        test (optional): np.ndarray
            To be used for early stopping if passed in. 

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
    eval_metric = return_scorer('auc_precision_recall')

    fit_params={}
    if test and (model_name == 'gboosting' or model_name == 'xgboost'):
        test_target, test_features = get_target_features(test)
        # The monitor callback and xgboost use code under the hood
        # that requires these changes. 
        test_target = test_target.values.astype('float32')  
        test_features = test_features.values.astype('float32')
        test_target = test_target.copy(order='C')
        test_features = test_features.copy(order='C')

        early_stopping_tolerance = 5
        fit_params = _prep_fit_params(model_name, fit_params, 
                early_stopping_tolerance, test_features, test_target)

    if random: 
        params = _get_random_params(model_name)
        grid_search = RandomizedSearchCV(estimator=model, param_distributions=params, 
                scoring=eval_metric, cv=cv_fold_generator, fit_params=fit_params, 
                n_iter=num_iterations)
    else: 
        params = _get_grid_params(model_name)
        grid_search = GridSearchCV(estimator=model, param_grid=params, 
                scoring='roc_auc', cv=cv_fold_generator, fit_params=fit_params)
    grid_search.fit(train_features.values, train_target.values)

    best_model = grid_search.best_estimator_
    best_mean_score = grid_search.best_score_
    scores = grid_search.grid_scores_

    return best_model, best_mean_score, scores

def run_keras_param_search(model, train, test, cv_fold_generator, 
        n_iter=5): 
    """Run parameter tuning with a keras model over the inputted folds. 

    Obtain a dictionary that will be used to generate parameter values
    randomly for each one of the folds in the cv_fold_generator. Then
    cycle over the `cv_fold_generator` `n_iter` number of times, each time 
    sampling from the dictionary a set of paramter values to use for 
    that particular iteration. 

    Along the way, save up the scores of each one of the iterations. When
    finished, fit the model using the best set of the paramters, and return 
    the "best model", a mean validation score across that model, and the 
    scores across all iterations (this is similar to what `GridSearchCV` 
    and `RandomizedSearchCV` from sklearn can return. 

    Args: 
    ----
        model: Keras model 
            A pre-built Keras model to be compiled and fit.  
        train: np.ndarry
        test: np.ndarry
        cv_fold_generator: list of tuples 
            Holds the train/test splits to be used for each fold during 
            cross-validation. 

    Returns: 
    -------
        best_model: Keras model. 
            The best model as obtained through the parameter search. 
        best_mean_score: float
            The mean validation score over the folds, from the best_model.  
        scores: list
            The scores from each run of the paramateter search over the 
            folds. 
    """
    
    train_features, train_target, test_features, test_target = \
            _prep_keras_inputs(train, test)

    for iteration in xrange(n_iter): 
        for train_split, test_split in cv_fold_generator: 
            X_train = train_features[train_split]
            y_train = train_target[train_split]
            X_test = train_features[test_split]
            y_test = train_target[test_split]

            model.fit(X_train, y_train, X_test=test_features, 
                    y_test=test_target, early_stopping=5)
            score = model.evaluate(X_test, y_test)
            scores.append(score)

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

def _prep_keras_inputs(train, test): 
    """Get the train/test data into the right format for Keras. 

    First, split the train and test into features and target.
    Next, since keras models only accept np.ndarray's, format the 
    training/test data to meet that. In addition, since this is a 
    classification problem and a `softmax` will be used at the final 
    layer, the test set needs to be fed in as two dimensional. 

    Args: 
    ----
        train: pandas DataFrame
        test: pandas DataFrame

    Return: 
    ------
        train_features: np.ndarray
        train_target: np.ndarray
        test_features: np.ndarray
        test_target: np.ndarray
    """
    
    # Break out the DataFrames. 
    train_target, train_features = get_target_features(train)
    test_target, test_features = get_target_features(test)
    
    # Format everything. 
    train_target = train_target.astype(int)
    train_target = np_utils.to_categorical(train_target)

    test_target = test_target.astype(int)
    test_target = np_utils.to_categorical(test_target)

    return train_features, train_target, test_features, test_target

def get_best_params(model_name): 
    """Return the model parameters to use for the final model.

    Args: 
    ----
        model_name: str
    """

    if model_name == 'random_forest': 
        best_params = {'n_estimators': 1, 
                'max_depth': 2}
    elif model_name == 'extra_trees': 
        best_params = {'n_estimators': 1, 
                'max_depth': 2}

    return best_params

