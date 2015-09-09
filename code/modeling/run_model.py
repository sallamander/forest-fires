import sys
from sklearn.linear_model import LogisticRegression
from scoring import return_scores
from data_manip import tt_splits

def get_model(model_name): 
	'''
	Input: String
	Output: Instantiated Model
	'''

	if model_name == 'logit': 
		lr = LogisticRegression()
		return lr

def fit_model(train_data, model_to_fit):
	'''
	Input: Pandas DataFrame, Instantiated Model
	Output: Fitted model

	Using the fire column as the target and the remaining columns as the features, fit 
	the inputted model. 
	'''

	target = train_data.fire
	features = train_data.drop('fire', axis=1)

	model_to_fit.fit(features, target)
	return model_to_fit

def predict_with_model(test_data, model): 
	'''
	Input: Pandas DataFrame, Fitted Model
	Output: Numpy Array of Predictions

	Using the fitted model, make predictions with the test data and return those predictions. 
	'''

	target = test_data.fire
	features = test_data.drop('fire', axis=1)

	predictions, predicted_probs = lr.predict(features), lr.predict_proba(features)

	return predictions, predicted_probs


if __name__ == '__main__': 
	# sys.argv[1] will hold the name of the model we want to run (logit, random forest, etc.), 
	# and sys.argv[2] will hold our input dataframe (data will all the features and target). 
	model_name = sys.argv[1]

	with open(sys.argv[2]) as f: 
		input_df = pickle.load(f)

	train, test = tt_splits(input_df)
	model = get_model(model_name)
	fitted_model = fit_model(train, model)
	preds, preds_probs = predict_with_model(test, fitted_model)


