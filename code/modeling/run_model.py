"""A driver module for running models. 

This module exists as the driver program to run any number
of models. It works through the following high level steps: 

* Reads in the data to use as well as the model to be run 
  from command line arguments
* It breaks the data into a train/test (validation/hold out) 
  split using an optionally inputted command line argument
* It performs any preprocessing on the data that needs to be
  done (e.g. normalization)
* It creates an iterator to use for CV. 
* It runs the model. 

The imported, custom built modules help substantially with 
all of this. 
"""

import sys
import time
import pickle
import pandas as pd
import numpy as np
from keras.utils import np_utils
from datetime import timedelta, datetime
from scoring import return_scorer
from time_val import SequentialTimeFold
from preprocessing import normalize_df, prep_data, \
        alter_nearby_fires_cols, get_target_features
from supervised.supervised_models import get_model 
from param_searching import run_sklearn_grid_search, \
    run_sklearn_random_search

def get_train_test(df, date_col, test_date): 
    """Return a train/test split based off the inputted test_date

    For the inputted DataFrame, break it into a train/test split, 
    where the train is all those rows prior to the test_date, and 
    the test is all the rows that fall on that day. 

    Args: 
    ----
        df: Pandas DataFrame
        date_col: str
            Holds the name of the date column in the `df` that 
            the train/test split will be made on. 
        test_date: datime.datime

    Return: 
    ------
        train: Pandas DataFrame
        test: Pandas DataFrame
    """

    # In the case that we are putting in a test_date for training, we 
    # want to make sure to only grab that day (and not days that are greater
    # than it, which will be present in training). 
    max_test_date = test_date + timedelta(days=1)

    # We're only going to go back 14 days to perform CV over. 
    min_train_date = test_date - timedelta(days=14)
    test_mask = np.where(np.logical_and(df[date_col] >= test_date, 
        df[date_col] < max_test_date))[0]
     
    train_mask = np.where(df[date_col] < test_date)[0]
    train = df.ix[train_mask, :] 
    test = df.ix[test_mask, :]

    return train, test

def get_model_args(model_name, train): 
    """Return the dictionary holding the kwargs passed to get_model.

    For the time being, this really just holds the args controlling the 
    fitting of the KerasNet (`supervised.keras_net.py`). 

    Args: 
    ----
        model_name: str

    Return: 
    ------
        model_kwargs: dct 
            Holds what kwargs to pass when instantiating the 
            inputted model type. 
    """

    model_kwargs = {}
    # This will be used as the random seed for all models. 
    model_kwargs['rand_seed'] = 24

    if model_name == 'neural_net': 
        # The -2 in the 'input_dim' below is because the `date_fire` and 
        # `fire_bool` column get dropped later, but are still in train at 
        # this point. 
        layer_1 = {'num': 1, 'nodes': 2, 'activation': 'softmax', 
                'input_dim': train.shape[1] - 2}
        model_kwargs['layer_1'] = layer_1
        model_kwargs['num_layers'] = 1

    return model_kwargs 

def log_results(model_name, train, best_fit_model, score, best_score): 
    """Log the results of our best model run. 

    Args: 
    ----
        model_name: str
        train: np.ndarray
            Holds the training data, used to store the column names. 
        fitted_model: variable 
            Holds the best fit model, used to store the final parameters
            of that model. 
        score: float 
            Score from the validation/hold out data set (not used at 
            all during cross validation). 
        best_roc_auc: float 
            Best score from the fitted model. 
    """

    st = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    filename = 'code/modeling/model_output/logs/' + model_name + '.txt'
    with open(filename, 'a+') as f:
        f.write(st + '\n')
        f.write('-' * 100 + '\n')
        f.write('Model Run: ' + model_name + '\n' * 2)
        f.write('Params: ' + str(best_fit_model.get_params()) + '\n' * 2)
        f.write('Features: ' + ', '.join(train.columns) + '\n' * 2)
        f.write('Test AUC_PR: ' + str(score) + '\n' * 2)
        f.write('Train AUC_PR: ' + str(best_score) + '\n' * 2)

if __name__ == '__main__': 
    # sys.argv[1] will hold the name of the model we want to run (logit, 
    # random forest, etc.), and sys.argv[2] will hold our input dataframe 
    # (data will all the features and target). 
    model_name = sys.argv[1]

    base_input_df = pd.read_csv(sys.argv[2], parse_dates=['date_fire'])
    with open('code/makefiles/columns_list.pkl') as f: 
        keep_columns = pickle.load(f)

    input_df = alter_nearby_fires_cols(base_input_df)
    input_df = input_df[keep_columns]
    if len(sys.argv) == 4: 
        # If this is 4, I'm expecting that a date was passed in that we want
        # to use for the day of our test set (i.e. the days fires that we are 
        # predicting). Otherwise, we'll use the most recent date in our df. 
        date_parts = sys.argv[3].split('-')
        test_set_date = datetime(int(date_parts[0]), 
                int(date_parts[1]), int(date_parts[2]), 0, 0, 0)
    else: 
        test_set_timestamp = input_df['date_fire'].max()
        test_set_date = datetime(test_set_timestamp.year, 
                test_set_timestamp.month, test_set_timestamp.day, 0, 0, 0)
    train, test = get_train_test(input_df, 'date_fire', test_set_date)
    # sklearn logit uses regularization by default, so it'd be best 
    # to scale the variables in that case as well. 
    if model_name == 'neural_net' or model_name == 'logit': 
        train = normalize_df(train)
        test = normalize_df(test)
    
    # If 'random' was passed in, then perform a random search from parameter
    # distributions, and else just do a grid search. 
    rand_search = True if len(sys.argv) == 5 and sys.argv[4] == 'random' \
            else False 

    # We need to reset the index so the time folds produced work correctly.
    # the test index is reset to get it to work below with Keras. 
    train.reset_index(drop=True, inplace=True)
    test.reset_index(drop=True, inplace=True)
    date_step_size = timedelta(days=1)
    model_kwargs = get_model_args(model_name, train)

    model = get_model(model_name, model_kwargs)
    
    cv_fold_generator = SequentialTimeFold(train, date_step_size, 14, 
            test_set_date, 'fire_bool')
    
    train, test = prep_data(train), prep_data(test)
    
    if model_name != 'neural_net': 
        best_fit_model, best_score, scores = \
            run_sklearn_param_search(model, train, test, list(cv_fold_generator),
                    rand_search, early_stopping_tolerance, model_name)
    else: 
        train_target, train_features = get_target_features(train)
        test_target, test_features = get_target_features(test)
        test_target = test_target.astype(int)
        test_target = np_utils.to_categorical(test_target)
        train_target = train_target.astype(int)
        train_target = np_utils.to_categorical(train_target)
        model.fit(train_features.values, train_target, 
                X_test=test_features.values, y_test=test_target, 
                early_stopping=5)

    scorer = return_scorer()
    test_target, test_features = get_target_features(test)
    score = scorer(best_fit_model, test_features, test_target)
    log_results(model_name, train, best_fit_model, score, best_score)
