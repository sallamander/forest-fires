from sklearn.linear_model import LogisticRegression 
from data_manip import tt_splits
from scoring import return_scores
import pickle

def fit_logistic(df):
	'''
	Input: PandasDataFrame
	Output: Fitted Sklearn Logistic Model
	'''

	lr = LogisticRegression()
	target = df.fire
	features = df.drop('fire', axis=1)

	lr.fit(features, target)
	return lr

def predict_with_logistic(lr, test_data): 
	'''
	Input: Fitted Logistic Model, Pandas DataFrame
	Output: Numpy Array of Predictions

	Using the fitted model, make predictions with the test data and return those predictions. 
	'''

	target = df.fire
	features = df.drop('fire', axis=1)

	predictions, predicted_probs = lr.predict(features), lr.predict_proba(features)

	return predictions, predicted_probs

if __name__ == '__main__': 
	with open('input_df.pkl') as f: 
		input_df = pickle.load(f)

	train, test = tt_splits(input_df)
	fitted_logit = fit_logistic(train)
	preds, pred_probs = predict_with_logistic(fitted_logit, test)
