import sys
import pickle
import pandas as pd
import numpy as np
import keras
from datetime import timedelta, datetime
from data_manip.time_val import SequentialTimeFold, StratifiedTimeFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.grid_search import GridSearchCV
from keras.models import Sequential

def get_train_test(df, date_col, days_back): 
    '''
    Input: Pandas DataFrame, String, Integer
    Output: Pandas DataFrame, Pandas DataFrame

    For the inputted DataFrame, take the max date (from the date_col), go 
    back days_back, and then split into train and test at that point. 
    All rows with a date prior to that split point are train and all rows 
    with a date after that split point are test. 
    '''

    max_date = df[date_col].max()
    split_point = max_date - timedelta(days=days_back)
    test_mask = df[date_col] >= split_point
    train, test = df.ix[~test_mask, :], df.ix[test_mask, :]

    return train, test

def get_model(model_name, train_data): 
    '''
    Input: String, Pandas DataFrame
    Output: Instantiated Model
    '''
    random_seed=24
    if model_name == 'logit': 
        return LogisticRegression(random_state=random_seed)
    elif model_name == 'random_forest': 
        return RandomForestClassifier(random_state=random_seed, n_jobs=2)
    elif model_name == 'gradient_boosting': 
        return GradientBoostingClassifier(random_state=random_seed)
    elif model_name == 'neural_net': 
        return get_neural_net(train_data)

def sklearn_grid_search(model_name, train_data, test_data, cv_fold_generator): 
    '''
    Input: String, Pandas DataFrame, Pandas DataFrame
    Output: Best fit model from grid search parameters. 

    For the given model name, grab a model and the relevant grid parameters, 
    perform a grid search with those grid parameters, and return the best 
    model. 
    '''

    model = get_model(model_name, train_data)
    if isinstance(model, keras.models.Sequential): 
        model = fit_neural_net(model, train_data, test_data)
        return model
    grid_parameters = get_grid_params(model_name)
    grid_search = GridSearchCV(estimator=model, param_grid=grid_parameters, 
            scoring='roc_auc', cv=cv_fold_generator)
    target, features = get_target_features(train_data)
    grid_search.fit(features, target)

    return grid_search.best_estimator_

def get_grid_params(model_name): 
    '''
    Input: String
    Output: Dictionary
    '''
    if model_name == 'logit': 
        return {'penalty': ['l2'], 'C': [0.1]}
    elif model_name == 'random_forest': 
        return {'n_estimators': [10], 
                'max_depth': [15]}
    elif model_name == 'gradient_boosting': 
        return {'n_estimators': [250], 
                'learning_rate': [0.1], 
                'min_samples_leaf': [250]}

def get_target_features(df): 
    '''
    Input: Pandas DataFrame
    Output: Numpy Array, Numpy Array

    For the given dataframe, grab the target and features (fire bool versus 
    all else) and return them. 
    '''

    target = df.fire_bool
    features = df.drop('fire_bool', axis=1)
    return target, features

if __name__ == '__main__': 
    # sys.argv[1] will hold the name of the model we want to run (logit, 
    # random forest, etc.), and sys.argv[2] will hold our input dataframe 
    # (data will all the features and target). 
    model_name = sys.argv[1]

    base_input_df = pd.read_csv(sys.argv[2], parse_dates=['date_fire'])
    with open('code/makefiles/columns_list.pkl') as f: 
        keep_columns = pickle.load(f)

    input_df = base_input_df[keep_columns]
    train, test = get_train_test(input_df, 'date_fire', 14) 
    
    # We need to reset the index so the time folds produced work correctly.
    train.reset_index(drop=True, inplace=True)
    train_dates = train['date_fire']
    date_step_size = timedelta(days=14)
    init_split_point = datetime(2013, 1, 1, 0, 0, 0)
    cv_fold_generator = SequentialTimeFold(train_dates, date_step_size, init_split_point)
    
    train.fillna(-999, inplace=True)
    train.replace(np.inf, -999, inplace=True)
    train.drop('date_fire', inplace=True, axis=1)
    sklearn_grid_search(model_name, train, test, cv_fold_generator) 

