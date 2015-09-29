from datetime import date
import pandas as pd

def tt_split_all_less_n_days(df, days_back=60): 
	'''
	Input: Pandas Dataframe, Integer
	Output: Pandas DataFrame, Pandas DataFrame

	Split the pandas data frame into a train/test split where we train on all of the 
    data but the most recent days_back days. 
	'''

	df['date_fire'] = pd.to_datetime(df['date_fire'])
	today = df['date_fire'].max().date()
	today_less_days = today - pd.Timedelta(days=days_back)
	train = df.query('date_fire < @today_less_days')
	test = df.query('date_fire >= @today_less_days')
	del train['date_fire']
	del test['date_fire']

	return train, test

def tt_split_early_late(df, year, months_forward): 
	'''
    Input: Pandas DataFrame, Integer
    Output: Pandas DataFrame, Pandas DataFrame 

    Take the pandas dataframe, and put all those data points in year year and any prior years into the training data.
    Also put all those months that are within months_forward past that year into the training data. For example, 
    if year is 2013 and months_foward is 3, take all data from year 2012 and 2013 and put that into the training 
    data. In addition, put the first 3 months of 2014 into the training data. Use the rest as the test data set.
    ''' 

    df['date_fire'] = pd.to_datetime(df['date_fire'])
    date_split = datetime.date(year, 1, 1) + pd.Timedelta(months=months_forward)
    train = df.query('date_fire.year() < @year or (date_fire.year() == (@year + 1) and date_fire.month() < @months_forward)) 


