from sklearn.linear_model import LogisticRegression 

def run_logistic(df):
	'''
	Input: PandasDataFrame
	Output: Fitted Sklearn Logistic Model
	'''

	lr = LogisticRegression()
	target = df.fire
	features = df.drop('fire', axis=1)

	lr.fit(features, target)
	return lr

if __name__ == '__main__': 
	pass 