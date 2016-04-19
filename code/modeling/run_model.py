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
from param_searching import run_sklearn_param_search

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
    max_test_date = test_date + timedelta(days=365)

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

def log_results(model_name, train, best_fit_model, best_score, scores): 
    """Log the results of our best model run. 

    Args: 
    ----
        model_name: str
        train: np.ndarray
            Holds the training data, used to store the column names. 
        fitted_model: variable 
            Holds the best fit model, used to store the final parameters
            of that model. 
        best_roc_auc: float 
            Best score from the fitted model. 
        scores: list 
            Scores from each model fit on the folds during cross-validation.
    """

    st = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    filename = 'code/modeling/model_output/logs/' + model_name + '.txt'
    with open(filename, 'a+') as f:
        f.write(st + '\n')
        f.write('-' * 100 + '\n')
        f.write('Model Run: ' + model_name + '\n' * 2)
        f.write('Params: ' + str(best_fit_model.get_params()) + '\n' * 2)
        f.write('Features: ' + ', '.join(train.columns) + '\n' * 2)
        f.write('Train AUC_PR: ' + str(best_score) + '\n' * 2)
        for score in scores: 
            str_to_write = str(score[0]) + ' : ' + str(score[1]) + '\n'
            f.write(str_to_write)

def log_scores(best_fit_model, hold_out_features, hold_out_target, 
        model_name, date_parts, hold_out_feats_pre_norm): 
    """Predict using the best fit model and save the scores. 

    Args: 
    ----
        best_fit_model: varied
            Holds a model that has a `fit` method. 
        hold_out_features: pandas DataFrame
        hold_out_target: pandas Series
        model_name: str
            Holds the name of the model fit, used for filepath 
            purposes. 
        date_parts: list of strings 
            Holds the date used for the hold out set, used for the 
            filepath purposes. 
        hold_out_feats_pre_norm: pandas DataFrame
            Holds the unormalized values (if necessary) to be merged
            back on. The merged values will be meaningless. 
    """

    st = datetime.fromtimestamp(time.time())
    preds_probs = best_fit_model.predict_proba(hold_out_features)
    preds_probs_df = pd.DataFrame(data=preds_probs, columns=['preds_probs_0', 
        'preds_probs_1'])
    hold_out_target_df = pd.DataFrame(data=hold_out_target, columns=['fire_bool'])
    
    master_df = pd.concat([hold_out_feats_pre_norm, 
        hold_out_target_df, preds_probs_df], axis=1)
    save_fp = 'code/modeling/model_output/preds/' + model_name + \
            '/preds_df_' + '-'.join([str(st.year), str(st.month), str(st.day)
                , str(st.hour), str(st.minute)])
    master_df.to_csv(save_fp, index=False)

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
    validation, hold_out = get_train_test(input_df, 'date_fire', test_set_date)

    # We need to reset the index so cross-validation happens appropriately. 
    validation.reset_index(drop=True, inplace=True)

    # sklearn logit uses regularization by default, so it'd be best 
    # to scale the variables in that case as well. 
    if model_name == 'neural_net' or model_name == 'logit': 
        validation = normalize_df(validation)
    
    # If 'random' was passed in, then perform a random search from parameter
    # distributions, and else just do a grid search. 
    rand_search = True if len(sys.argv) == 5 and sys.argv[4] == 'random' \
            else False 

    date_step_size = timedelta(days=30)
    model_kwargs = get_model_args(model_name, validation)

    model = get_model(model_name, model_kwargs)
    
    cv_fold_generator = SequentialTimeFold(df=validation, step_size=date_step_size, 
            max_folds=11, test_set_date=test_set_date,  
            days_forward=30, y_col='fire_bool')

    validation = prep_data(validation)
    
    if model_name != 'neural_net': 
        best_fit_model, best_score, scores = \
            run_sklearn_param_search(model, validation, list(cv_fold_generator),
                    rand_search, model_name)
    else: 
        best_fit_model, best_score, scores = \
            run_keras_param_search(model, validation, list(cv_fold_generator))
                    
    log_results(model_name, validation, best_fit_model, best_score, scores)
    # log_scores(best_fit_model, hold_out_features, hold_out_target, model_name, 
    # date_parts, hold_out_feats_pre_norm)
