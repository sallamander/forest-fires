import sys
import pickle
import pandas as pd
import numpy as np
import keras
import time
from scoring import return_scores
from datetime import timedelta, datetime
from time_val import SequentialTimeFold, StratifiedTimeFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.grid_search import GridSearchCV
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import SGD, RMSprop
from keras.utils import np_utils

def get_train_test(df, date_col, days_back, test_date): 
    '''
    Input: Pandas DataFrame, String, Integer
    Output: Pandas DataFrame, Pandas DataFrame

    For the inputted DataFrame, take the max date (from the date_col), go 
    back days_back, and then split into train and test at that point. 
    All rows with a date prior to that split point are train and all rows 
    with a date after that split point are test. 
    '''
    
    # In the case that we are putting in a test_date for training, we 
    # want to make sure to only grab that day (and not days that are greater
    # than it, which will be present in training). 
    max_test_date = test_date + timedelta(days=1)
    min_test_date = test_date - timedelta(days=days_back)
    test_mask = np.where(np.logical_and(df[date_col] >= test_date, 
        df[date_col] < max_test_date))[0]
    train_mask = np.where(np.logical_and(df[date_col] < test_date, 
        df[date_col] >= min_test_date))[0]
    train, test = df.ix[train_mask, :], df.ix[test_mask, :]

    return train, test

def normalize_df(input_df): 
    '''
    Input: Pandas DataFrame
    Output: Pandas DataFrame
    '''

    input_df2 = input_df.copy()
    for col in input_df.columns: 
        if col not in ('fire_bool', 'date_fire'): 
            input_df2[col] = (input_df[col] - input_df[col].mean()) \
                / input_df[col].std()

    return input_df2

def prep_data(df): 
    '''
    Input: Pandas DataFrame 
    Output: Pandas DataFrame

    Fill in N/A's and inf. values, and make sure to drop the 'date_fire'
    column. 
    '''

    df.fillna(-999, inplace=True)
    df.replace(np.inf, -999, inplace=True)
    df.drop('date_fire', inplace=True, axis=1)

    return df

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

    return grid_search.best_estimator_, grid_search.grid_scores_[0][1]

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

def get_neural_net(train_data): 
    '''
    Input: Integer, Pandas DataFrame
    Output: Instantiated Neural Network model

    Instantiate the neural net model and output it to train with. 
    '''

    np.random.seed(24)
    hlayer_1_nodes = 250
    hlayer_2_nodes = 115
    hlayer_3_nodes = 100
    hlayer_4_nodes = 100
    model = Sequential()
    
    input_dim = train_data.shape[1] - 1 
    model.add(Dense(hlayer_1_nodes, input_dim=input_dim, init='uniform'))
    model.add(Activation('relu'))
    model.add(Dropout(0.35))
    model.add(Dense(hlayer_2_nodes, init='uniform'))
    model.add(Activation('relu'))
    model.add(Dropout(0.35))
    model.add(Dense(hlayer_3_nodes, init='uniform'))
    model.add(Activation('relu'))
    model.add(Dropout(0.35))
    model.add(Dense(2, init='uniform'))
    model.add(Activation('softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='RMSprop')

    return model

def get_grid_params(model_name): 
    '''
    Input: String
    Output: Dictionary
    '''
    if model_name == 'logit': 
        return {'penalty': ['l2'], 'C': [0.05, 0.1, 0.15]}
    elif model_name == 'random_forest': 
        return {'n_estimators': [800, 1000, 1200], 
                'max_depth': [10, 15, 20]}
    elif model_name == 'gradient_boosting': 
        return {'n_estimators': [250], 
                'learning_rate': [0.01, 0.05, 0.1], 
                'min_samples_leaf': [200, 250, 300]}

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

def fit_neural_net(model, train_data, test_data):  
    '''
    Input: Instantiated Neural Network, Pandas DataFrame, Pandas DataFrame
    Output: Fitted model 
    '''

    np.random.seed(24)
    train_target, train_features = get_target_features(train_data)
    test_target, test_features = get_target_features(test_data)
    train_target = np_utils.to_categorical(train_target, 2) 
    test_target = np_utils.to_categorical(test_target, 2) 
    train_features, test_features = train_features.values, test_features.values
    model.fit(train_features, train_target, batch_size=100, 
            nb_epoch=10, verbose=1)
    return model

def predict_with_model(test_data, model): 
    '''
    Input: Pandas DataFrame, Fitted Model
    Output: Numpy Array of Predictions

    Using the fitted model, make predictions with the test data and return those predictions. 
    '''

    if isinstance(model, keras.models.Sequential): 
        target, features = get_target_features(test_data)
        predictions = model.predict(features.values)[:, 1] > 0.50 
        predicted_probs = model.predict_proba(features.values)
    else: 
        target, features = get_target_features(test_data)
        predictions = model.predict(features)
        predicted_probs = model.predict_proba(features)

    return predictions, predicted_probs

def log_results(model_name, train, fitted_model, scores, best_roc_auc, run_time): 
    '''
    Input: String, Pandas DataFrame,  Dictionary, Numpy Array, Float  
    Output: .txt file. 

    Log the results of this run to a .txt file, saving the column names (so I know what features I used), 
    the model name (so I know what model I ran), the parameters for that model, 
    and the scores associated with it (so I know how well it did). 
    '''

    st = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    filename = 'code/modeling/model_output/logs/' + model_name + '.txt'
    with open(filename, 'a+') as f:
        f.write(st + '\n')
        f.write('-' * 100 + '\n')
        f.write('Model Run: ' + model_name + '\n' * 2)
        f.write('Params: ' + str(fitted_model.get_params()) + '\n' * 2)
        f.write('Features: ' + ', '.join(train.columns) + '\n' * 2)
        f.write('Scores: ' + str(scores) + '\n' * 2)
        f.write('Validation ROC AUC: ' + str(best_roc_auc) + '\n' * 2)
        f.write('Run time: ' + str(run_time) + '\n' * 2)


if __name__ == '__main__': 
    # sys.argv[1] will hold the name of the model we want to run (logit, 
    # random forest, etc.), and sys.argv[2] will hold our input dataframe 
    # (data will all the features and target). 
    model_name = sys.argv[1]

    base_input_df = pd.read_csv(sys.argv[2], parse_dates=['date_fire'])
    with open('code/makefiles/columns_list.pkl') as f: 
        keep_columns = pickle.load(f)

    input_df = base_input_df[keep_columns]
    if len(sys.argv) == 4: 
        # If this is 4, I'm expecting that a date was passed in that we want
        # to use for the day of our test set (i.e. the days fires that we are 
        # predicting). Otherwise, we'll use the most recent date in our df. 
        date_parts = sys.argv[4].split('-')
        test_set_date = datetime(date_parts[0], date_parts[1], date_parts[2],
                0, 0, 0)
    else: 
        test_set_timestamp = input_df['date_fire'].max()
        test_set_date = datetime(test_set_timestamp.year, 
                test_set_timestamp.month, test_set_timestamp.day, 0, 0, 0)
    train, test = get_train_test(input_df, 'date_fire', 14, test_set_date)

    if model_name == 'neural_net': 
        train = normalize_df(train)
        test = normalize_df(test)

    
    # We need to reset the index so the time folds produced work correctly.
    train.reset_index(drop=True, inplace=True)
    train_dates = train['date_fire']
    date_step_size = timedelta(days=14)
    init_split_point = datetime(2013, 1, 1, 0, 0, 0)
    cv_fold_generator = SequentialTimeFold(train_dates, date_step_size, init_split_point)
    
    train = prep_data(train)
    test = prep_data(test)
    start = time.time()
    best_fit_model, mean_metric_score = \
            sklearn_grid_search(model_name, train, test, cv_fold_generator) 
    end = time.time()
    run_time = end - start
    preds, preds_probs = predict_with_model(test, best_fit_model)
    scores = return_scores(test.fire_bool, preds, preds_probs)
    log_results(model_name, train, best_fit_model, scores, mean_metric_score, 
            run_time)


