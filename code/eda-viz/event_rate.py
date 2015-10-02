'''
What I'm seeing is that the past 60 days of my data set have a much larger event rate 
(i.e. larger percentage of forest fires) than the rest of my data set). This here 
is just going to check out the event rate by different splits of the train/test data. 
'''

import pickle
import pandas as pd
import datetime
import numpy as np

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
	# If we want more than 12 months forward, then we want a whole nother year, so let's just adjust the 
	# year and months_forward variables to handle that. 
	if months_forward >= 12: 
		year += 1
		months_forward -= 12
	date_split = datetime.date(year + 1, 1, 1)
	date_split = return_next_month_start(date_split, months_forward)

	train = df.query('date_fire < @date_split')
	test = df.query('date_fire >= @date_split')

	return train, test

def return_next_month_start(t, n): 
	'''
	Input: datetime.date
	Output: datetime.date

	For the given datetime.date, return a datetime.date object that is the date for the first day in the 
	nth month ahead. For example, if I feed in January and the number 3, then I want this to spit back a 
	datetime.date that is the first day of the month of April in the same year.
	'''

	# Go ahead and move the inputted time forward at least 27 days forward for the number of months 
	# that we want. We know that there are at least 27 days in each month, and that this step will 
	# put us only a handful of days before the start of the month we want. We can then step through 
	# day by day until the month changes. 
	if n == 0: 
		return t

	t = t + datetime.timedelta(days=(27 * n))

	one_day = datetime.timedelta(days=1)
	one_month_later = t + one_day 

	while one_month_later.month == t.month: 
		one_month_later += one_day

	return one_month_later



if __name__ == '__main__': 

	with open('../modeling/input_df_0.1.pkl') as f: 
		input_df = pickle.load(f)

	days_back = 60
	train, test = tt_split_all_less_n_days(input_df, days_back=days_back)

	test_event_rate = test.fire_bool.mean()
	train_event_rate = train.fire_bool.mean()
	training_event_rate = []
	validation_event_rate = []

	for months_forward in xrange(0, 31, 3): 
		training_set, validation_set = tt_split_early_late(train, 2012, months_forward)
		training_event_rate.append(training_set.fire_bool.mean())
		validation_event_rate.append(validation_set.fire_bool.mean())


	train_rate = np.array(training_event_rate)
	test_rate = np.array(validation_event_rate)

	print test_event_rate
	print train_event_rate
	print training_event_rate
	print validation_event_rate

	print train_rate > test_rate

	for month in xrange(1, 13): 
		if month < 10: 
			col = 'month_0' + str(month)
		else: 
			col = 'month_' + str(month)
		vals = input_df.query(col + '== 1')
		print col, vals.fire_bool.mean()

