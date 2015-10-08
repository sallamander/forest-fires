import sys
import pickle
import time
import datetime
import keras
import numpy as np
import os
import pandas as pd
import itertools
from collections import defaultdict
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from scoring import return_scores
from data_manip.tt_splits import tt_split_all_less_n_days, tt_split_early_late
from sklearn.grid_search import GridSearchCV
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import SGD, RMSprop
from keras.utils import np_utils


def get_model(model_name, train_data): 
	'''
	Input: String, Pandas DataFrame
	Output: Instantiated Model
	'''
	random_seed=24
	if model_name == 'logit': 
		return LogisticRegression(random_state=random_seed)
	elif model_name == 'random_forest': 
		return RandomForestClassifier(random_state=random_seed, n_jobs=5)
	elif model_name == 'gradient_boosting': 
		return GradientBoostingClassifier(random_state=random_seed)
	elif model_name == 'neural_net': 
		return get_neural_net(train_data)

def fit_model(train_data, model_to_fit):
	'''
	Input: Pandas DataFrame, Instantiated Model
	Output: Fitted model

	Using the fire column as the target and the remaining columns as the features, fit 
	the inputted model. 
	'''

	target, features = get_target_features(train_data)

	model_to_fit.fit(features, target)
	return model_to_fit

def predict_with_model(test_data, model): 
	'''
	Input: Pandas DataFrame, Fitted Model
	Output: Numpy Array of Predictions

	Using the fitted model, make predictions with the test data and return those predictions. 
	'''

	if isinstance(model, keras.models.Sequential): 
		target, features = get_target_features(test_data)
		predictions, predicted_probs = model.predict(features.values)[:, 1] > 0.50, model.predict_proba(features.values)
	else: 
		target, features = get_target_features(test_data.drop('date_fire', axis=1))
		predictions, predicted_probs = model.predict(features), model.predict_proba(features)

	return predictions, predicted_probs

def log_results(model_name, train, fitted_model, scores, best_roc_auc): 
	'''
	Input: String, Pandas DataFrame,  Dictionary, Numpy Array, Float  
	Output: .txt file. 

	Log the results of this run to a .txt file, saving the column names (so I know what features I used), 
	the model name (so I know what model I ran), the parameters for that model, 
	and the scores associated with it (so I know how well it did). 
	'''

	st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
	filename = './modeling/logs/' + model_name + '.txt'
	with open(filename, 'a+') as f:
		f.write(st + '\n')
		f.write('-' * 100 + '\n')
		f.write('Model Run: ' + model_name + '\n' * 2)
		f.write('Params: ' + str(fitted_model.get_params()) + '\n' * 2)
		f.write('Features: ' + ', '.join(train.columns) + '\n' * 2)
		f.write('Scores: ' + str(scores) + '\n' * 2)
		f.write('Validation ROC AUC: ' + str(best_roc_auc) + '\n' * 2)

def sklearn_grid_search(model_name, train_data, test_data): 
	'''
	Input: String, Pandas DataFrame, Pandas DataFrame
	Output: Best fit model from grid search parameters. 

	For the given model name, grab a model and the relevant grid parameters, perform a grid search 
	with those grid parameters, and return the best model. 
	'''

	model = get_model(model_name, train_data)
	if isinstance(model, keras.models.Sequential): 
		model = fit_neural_net(model, train_data, test_data)
		return model
	grid_parameters = get_grid_params(model_name)
	grid_search = GridSearchCV(estimator=model, param_grid=grid_parameters, scoring='roc_auc', cv=10)
	target, features = get_target_features(train_data)
	grid_search.fit(features, target)

	return grid_search.best_estimator_

def own_grid_search(model_name, train_data, test_data): 
	'''
	Input: String, Pandas DataFrame, Pandas DataFrame
	Output: Best fit model from grid search of parameters. 
	'''
	model = get_model(model_name, train_data)
	if isinstance(model, keras.models.Sequential): 
	    model =  fit_neural_net(model, train_data, test_data)
	    return model
	roc_auc_scores_list = []  
	grid_parameters = get_grid_params(model_name)
	param_names, param_combs = prepare_grid_params(grid_parameters)  
	for idx, param_comb in enumerate(param_combs): 
		output_dict = defaultdict(list)
		param_dict = {}
		output_dict['model'] = idx
		for idx, param in enumerate(param_names): 
			output_dict[param] = param_comb[idx]
			param_dict[param] = param_comb[idx]
		for months_forward in xrange(0, 31, 3): 
			training_set, validation_set = tt_split_early_late(train_data, 2012, months_forward, months_backward=13)
			model = fit_model(model, param_dict, training_set.drop('date_fire', axis=1))
			roc_auc_score = predict_score_model(model, validation_set.drop('date_fire', axis=1))
			output_dict['roc_auc'].append(roc_auc_score)
		roc_auc_scores_list.append(output_dict)
   
	roc_save_filename = './model_output/roc_auc2_' + model_name
	with open(roc_save_filename, 'w+') as f: 
		pickle.dump(roc_auc_scores_list, f)
	best_params, best_roc_auc = return_best_params(roc_auc_scores_list) 
	model = fit_model(model, best_params, train_data.drop('date_fire', axis=1))

	return model, best_roc_auc

def prepare_grid_params(grid_parameters): 
	'''
	Input: Dictionary (of grid parameters)
	Output: List, List

	For the given grid of parameters inputted, output a list that holds the names of each parameter, 
	and another list that holds all of the possible combinations of those parameters (its these we will
	cycle through). 
	'''
	param_names, param_values = [], []
	key_val_pairs = grid_parameters.items()

	for key_val_pair in key_val_pairs: 
		param_names.append(key_val_pair[0])
		param_values.append(key_val_pair[1])
	
	param_combs =list(itertools.product(*param_values))

	return param_names, param_combs

def fit_model(model, param_dict, training_set): 
	'''
	Input: Instantiated Model, dictionary, Pandas DataFrame
	Output: Fitted Model

	Set the parameters for the instantiated model using the param_dict dictionary, and train it 
	using the training data in the pandas dataframe. 
	'''

	target, features = get_target_features(training_set)
	model.set_params(**param_dict)
	model.fit(features, target)

	return model

def predict_score_model(model, validation_set): 
	'''
	Input: Instantiated and fitted model, Pandas DataFrame
	Output: Floating point number	

	Obtain predicted probabilities for the test data set, and then an roc_auc score for how good 
	those probabilities were. 
	'''

	target, features = get_target_features(validation_set)
	preds, preds_probs = model.predict(features), model.predict_proba(features)
	scores = return_scores(target, preds, preds_probs)

	return scores['roc_auc_score']

def return_best_params(roc_auc_scores_list):
	'''
	Input: List of Dictionaries 
	Output: Dictionary, Float

	For the inputted dictionaries, cycle through them and pick the parameters that gave the highest set of 
	mean auc_scores accross the folds of CV. Each dictionary contains a list of roc_auc scores, a model number, 
	and the parameters for that model. We want to find the one with the highest mean roc_auc scores, and then 
	return a dictionary of only the parameters for that model. 
	'''
	max_mean_roc_auc = 0
	final_params_list = {}

	for roc_auc_dict in roc_auc_scores_list: 
	    mean_roc_auc = np.mean(roc_auc_dict['roc_auc'])
	    if mean_roc_auc > max_mean_roc_auc: 
	        max_mean_roc_auc = mean_roc_auc
	        del roc_auc_dict['model']
	        del roc_auc_dict['roc_auc']
	        final_params_list = roc_auc_dict


	return final_params_list, mean_roc_auc


def fit_neural_net(model, train_data, test_data):  
    '''
    Input: Instantiated Neural Network, Pandas DataFrame, Pandas DataFrame
    Output: Fitted model 
    '''

    np.random.seed(24)
    train_target, train_features = get_target_features(train_data)
    test_target, test_features = get_target_features(test_data)
    train_target, test_target = np_utils.to_categorical(train_target, 2), np_utils.to_categorical(test_target, 2) 
    train_features, test_features = train_features.values, test_features.values
    model.fit(train_features, train_target, batch_size=100, nb_epoch=10, validation_data=(test_features, test_target))
    return model

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

	model.add(Dense(train_data.shape[1] - 1, hlayer_1_nodes, init='uniform'))
	model.add(Activation('relu'))
	model.add(Dropout(0.35))
	model.add(Dense(hlayer_1_nodes, hlayer_2_nodes, init='uniform'))
	model.add(Activation('relu'))
	model.add(Dropout(0.35))
	model.add(Dense(hlayer_2_nodes, hlayer_3_nodes, init='uniform'))
	model.add(Activation('relu'))
	model.add(Dropout(0.35))
	model.add(Dense(hlayer_3_nodes, 2, init='uniform'))
	model.add(Activation('softmax'))

	model.compile(loss='categorical_crossentropy', optimizer='RMSprop')

	return model

def get_grid_params(model_name): 
	'''
	Input: String
	Output: Dictionary
	'''
	if model_name == 'logit': 
		return {'penalty': ['l2'], 'C': [0.1]}
	elif model_name == 'random_forest': 
		return {'n_estimators': [1000], 
				'max_depth': [15]}
	elif model_name == 'gradient_boosting': 
		return {'n_estimators': [250], 
		'learning_rate': [0.1], 
		'min_samples_leaf': [250]}

def get_target_features(df): 
	'''
	Input: Pandas DataFrame
	Output: Numpy Array, Numpy Array	

	For the given dataframe, grab the target and features (fire bool versus all else) and return them. 
	'''

	target = df.fire_bool
	features = df.drop('fire_bool', axis=1)
	return target, features

def output_model_preds(filename, model_name, preds_probs, test_df): 
	'''
	Input: String, Instantiated Model, Predicted Probability, Boolean 
	Output: CSV
	'''

	test_df[model_name] = preds_probs[:, 1]
	test_df.to_csv(filename, index=False)

def normalize_df(input_df): 
	'''
	Input: Pandas DataFrame
	Output: Pandas DataFrame
	'''

	input_df2 = input_df.copy()
	for col in input_df.columns: 
		if col != 'fire_bool': 
			input_df2[col] = (input_df[col] - input_df[col].mean()) / input_df[col].std()

	return input_df

if __name__ == '__main__': 
	# sys.argv[1] will hold the name of the model we want to run (logit, random forest, etc.), 
	# and sys.argv[2] will hold our input dataframe (data will all the features and target). 
	model_name = sys.argv[1]

	with open(sys.argv[2]) as f: 
		input_df = pickle.load(f)

	days_back = 60
	train, test = tt_split_all_less_n_days(input_df, days_back=days_back)

	if model_name == 'neural_net': 
		train = normalize_df(train.drop('date_fire', axis=1))
		test = normalize_df(test.drop('date_fire', axis=1))

	'''
	keep_list = ['conf']
	train = train[keep_list]
	test = test[keep_list]
	train = train.drop(keep_list, axis=1)
	test = test.drop(keep_list, axis=1)
	'''
	
	fitted_model, best_roc_auc = own_grid_search(model_name, train, test)
	'''
	roc_save_filename = 'roc_auc_' + model_name
	with open(roc_save_filename, 'w+') as f: 
		pickle.dump(roc_auc_scores, f)
	'''
	preds, preds_probs = predict_with_model(test, fitted_model)
	scores = return_scores(test.fire_bool, preds, preds_probs)
	log_results(model_name, train.drop('date_fire', axis=1), fitted_model, scores, best_roc_auc)

	filename = './model_output/' + model_name + '_preds_probs2.csv'
	output_model_preds(filename, model_name, preds_probs, test)



