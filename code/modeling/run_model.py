"""A driver module for running models. 

This module exists as the driver program to run any number of models. It works 
through the following high level steps: 

* Reads in the data to use as well as the model to be run from command line 
  arguments
* It breaks the data into a train/test (validation/hold out) split using an 
  optionally inputted command line argument
* It performs any preprocessing on the data that needs to be done (e.g. 
  normalization)
* It creates an iterator to use for CV. 
* It runs the model. 

The imported, custom built modules help substantially with all of this. 
"""

import sys
import time
import pickle
import pandas as pd
import numpy as np
from datetime import timedelta, datetime
from scoring import return_scorer, return_score
from time_val import SequentialTimeFold
from preprocessing import normalize_df, prep_data, \
        alter_nearby_fires_cols, get_target_features
from supervised_models import get_model 
from param_searching import run_sklearn_param_search, get_best_params
from model_logging import log_train_results, log_test_results, log_feat_importances

def format_date(dt): 
    """Return a datetime object from the inputted string. 

    Args: 
    ----
        dt: str

    Return: 
    ------
        formatted_date: datetime.datetime object
    """

    date_parts = dt.split('-')
    formatted_date = datetime(int(date_parts[0]), 
            int(date_parts[1]), int(date_parts[2]), 0, 0, 0)
    
    return formatted_date

def get_train_test(df, date_col, test_date): 
    """Return a train/test split based off the inputted test_date

    For the inputted DataFrame, break it into a train/test split, where the 
    train is all those rows prior to the test_date, and the test is all the 
    rows that fall on that day. 

    Args: 
    ----
        df: Pandas DataFrame
        date_col: str
        test_date: datime.datime

    Return: 
    ------
        train: Pandas DataFrame
        test: Pandas DataFrame
    """

    min_test_date = test_date
    max_test_date = min_test_date + timedelta(days=1)
    
    test_mask = np.where(np.logical_and(df[date_col] >= min_test_date, 
        df[date_col] < max_test_date))[0]
    train_mask = np.where(df[date_col] < min_test_date)[0]
    train = df.ix[train_mask, :] 
    test = df.ix[test_mask, :]

    return train, test

if __name__ == '__main__': 
    model_name = sys.argv[1]
    input_df_fp = sys.argv[2]

    base_input_df = pd.read_csv(input_df_fp, parse_dates=['date_fire'])
    with open('code/makefiles/columns_list.pkl') as f: 
        keep_columns = pickle.load(f)

    input_df = alter_nearby_fires_cols(base_input_df)
    input_df = input_df[keep_columns]
    if 'train' in sys.argv: 
        if len(sys.argv) == 4: 
            # If this is 4, use the passed in day as the date for the test set.  
            dt = sys.argv[3]
            test_set_date = format_date(dt)
        else: 
            test_set_timestamp = input_df['date_fire'].max()
            test_set_date = datetime(test_set_timestamp.year, 
                    test_set_timestamp.month, test_set_timestamp.day, 0, 0, 0)
        validation, hold_out = get_train_test(input_df, 'date_fire', test_set_date)

        # We need to reset the index so cross-validation happens appropriately. 
        validation.reset_index(drop=True, inplace=True)

        # sklearn logit uses regularization by default. 
        if model_name == 'logit': 
            validation = normalize_df(validation)
        
        # If 'random' was passed in, then perform a random param search and else 
        # just do a grid search. 
        rand_search = True if len(sys.argv) == 5 and sys.argv[4] == 'random' \
                else False 

        date_step_size = timedelta(days=30)
        model = get_model(model_name)
        cv_fold_generator = SequentialTimeFold(df=validation,       
                                               step_size=date_step_size, 
                                               max_folds=11, 
                                               test_set_date=test_set_date, 
                                               y_col='fire_bool', 
                                               days_forward=30)

        validation = prep_data(validation)
        best_fit_model, best_score = \
                run_sklearn_param_search(model, validation, list(cv_fold_generator),
                                         model_name, rand_search)
        score_type = 'AUC PR'              
        log_train_results(model_name, validation, best_fit_model, best_score,       
                          score_type)
    else: 
        beg_dt, end_dt = sys.argv[3], sys.argv[4]
        beg_date, end_date = format_date(beg_dt), format_date(end_dt)

        model = get_model(model_name)

        best_params = get_best_params(model_name)
        model.set_params(**best_params)

        dt_range = pd.date_range(beg_date, end_date)
        for dt in dt_range: 
            validation, hold_out = get_train_test(input_df, 'date_fire', dt)
            validation, hold_out = prep_data(validation), prep_data(hold_out)
            Y_train, X_train = get_target_features(validation)
            Y_test, X_test = get_target_features(hold_out)
            # Don't run models if there are no obs for a day. 
            if X_train.shape[0] and X_test.shape[0]: 
                model.fit(X_train, Y_train)
                pred_probs = model.predict_proba(X_test)[:, 1]
                roc_auc, pr_auc = None, None
                # We can't get area under the curve if there are no fires :(. 
                if Y_test.sum() != 0: 
                    roc_auc = return_score('auc_roc', pred_probs, Y_test)
                    pr_auc = return_score('auc_precision_recall', pred_probs, Y_test)
                log_feat_importances(model, X_train, dt)
                log_test_results(dt, Y_test, pred_probs, roc_auc, pr_auc)
