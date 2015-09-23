from datetime import date
import pandas as pd

def tt_split_all_less_n_days(df, days_back=60): 
	'''
	Input: Pandas Dataframe, Integer
	Output: Pandas DataFrame, Pandas DataFrame

	Split the pandas data frame into a train/test split where we train on all of the 
	data but the most recent 60 days
	'''

	df['date_fire'] = pd.to_datetime(df['date_fire'])
	today = df['date_fire'].max().date()
	today_less_days = today - pd.Timedelta(days=days_back)
	train = df.query('date_fire < @today_less_days')
	test = df.query('date_fire >= @today_less_days')
	del train['date_fire']
	del test['date_fire']

	return train, test

def tt_split_early_late(): 
	pass