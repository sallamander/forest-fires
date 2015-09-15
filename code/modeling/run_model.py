import sys
import pickle
import time
import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from scoring import return_scores
from data_manip.tt_splits import tt_split_all_less60
from sklearn.grid_search import GridSearchCV


def get_model(model_name): 
	'''
	Input: String
	Output: Instantiated Model
	'''
	if model_name == 'logit': 
		return LogisticRegression
	elif model_name == 'random_forest': 
		return RandomForestClassifier
	elif model_name == 'gradient_boosting': 
		return GradientBoostingClassifier

def fit_model(train_data, model_to_fit):
	'''
	Input: Pandas DataFrame, Instantiated Model
	Output: Fitted model

	Using the fire column as the target and the remaining columns as the features, fit 
	the inputted model. 
	'''

	target = train_data.fire_bool
	features = train_data.drop('fire_bool', axis=1)

	model_to_fit.fit(features, target)
	return model_to_fit

def predict_with_model(test_data, model): 
	'''
	Input: Pandas DataFrame, Fitted Model
	Output: Numpy Array of Predictions

	Using the fitted model, make predictions with the test data and return those predictions. 
	'''

	target = test_data.fire_bool
	features = test_data.drop('fire_bool', axis=1)

	predictions, predicted_probs = model.predict(features), model.predict_proba(features)

	return predictions, predicted_probs

def log_results(model_name, train, fitted_model, scores): 
	'''
	Input: String, Pandas DataFrame,  Dictionary
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

def grid_search(model_name, train_data): 
	'''
	Input: String
	Output: Best fit model from grid search parameters. 

	For the given model name, grab a model and the relevant grid parameters, perform a grid search 
	with those grid parameters, and return the best model. 
	'''

	model = get_model(model_name)
	grid_parameters = get_grid_params(model_name)
	grid_search = GridSearchCV(model, grid_parameters, scoring='roc_auc')
	grid_search.fit()



def get_grid_params(model_name): 
	'''
	Input: String
	Output: Dictionary
	'''
	if model_name == 'logit': 
		return {'penalty': ['l2', 'l1'], 'tol': [0.0001, 0.001, 0.01, 0.00001]}
	elif model_name == 'random_forest': 
		return {'n_estimators': [10, 50, 100, 250 , 500], 
				'max_depth': [None, 3, 5, 10], 
				'max_features': ['auto', None, 'log2']}
	elif model_name == 'gradient_boosting': 
		return {'learning_rate': [0.01, 0.1, 0.001], 
				'n_estimators': [100, 250, 500], 
				'max_depth': [None, 3, 5, 10], 
				'max_features': ['auto', None, 'log2']}

if __name__ == '__main__': 
	# sys.argv[1] will hold the name of the model we want to run (logit, random forest, etc.), 
	# and sys.argv[2] will hold our input dataframe (data will all the features and target). 
	model_name = sys.argv[1]

	with open(sys.argv[2]) as f: 
		input_df = pickle.load(f)
	
	train, test = tt_split_all_less60(input_df)

	'''
	keep_list = ['conf', 'fire_bool']
	train = train[keep_list]
	test = test[keep_list]
	train = train.drop(keep_list, axis=1)
	test = test.drop(keep_list, axis=1)
	'''

	model = grid_search(model, model_name)
	fitted_model = fit_model(train, model)
	preds, preds_probs = predict_with_model(test, fitted_model)
	scores = return_scores(test.fire_bool, preds, preds_probs)
	log_results(model_name, train, fitted_model, scores)




