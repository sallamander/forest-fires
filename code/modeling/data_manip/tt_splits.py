from datetime import date
import pandas as pd

def tt_split_all_less60(df): 
	'''
	Input: Pandas Dataframe
	Output: Pandas DataFrame, Pandas DataFrame

	Split the pandas data frame into a train/test split where we train on all of the 
	data but the most recent 60 days
	'''

	df['date'] = pd.to_datetime(df['date'])
	today = date.today()
	today_less60 = today - pd.Timedelta(days=60)
	train = df.query('date < @today_less60')
	test = df.query('date >= @today_less60')
	del train['date']
	del test['date']

	return train, test

def tt_split_early_late(): 
	pass