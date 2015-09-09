from datetime import date
from pandas import Timedelta

def tt_split_all_less60(df): 
	'''
	Input: Pandas Dataframe
	Output: Pandas DataFrame, Pandas DataFrame

	Split the pandas data frame into a train/test split where we train on all of the 
	data but the most recent 60 days
	'''

	today = date.today()
	today_less60 = today - Timedelta(days=60)
	train = df.query('date < @today_less60')
	test = df.query('date >= @today_less60')

	return train, test

def tt_split_early_late(): 
	pass