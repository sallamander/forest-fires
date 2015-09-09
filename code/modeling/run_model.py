import sys
from sklearn.linear_model import LogisticRegression

def get_model(model_name): 
	'''
	Input: String
	Output: Instantiated Model
	'''

	if model_name == 'logit': 
		lr = LogisticRegression()
		return lr

def fit_model(df, model_to_fit):
	'''
	Input: PandasDataFrame
	Output: Fitted model
	'''

	target = df.fire
	features = df.drop('fire', axis=1)

	model_to_fit.fit(features, target)
	return model_to_fit


if __name__ == '__main__': 
	model_name = sys.argv[1]