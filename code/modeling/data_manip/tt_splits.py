import pandas as pd
import datetime
import operator

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

def tt_split_early_late(df, input_date_split, months_forward, months_backward=None, year=True, days_forward=None): 
	'''
	Input: Pandas DataFrame, Integer
	Output: Pandas DataFrame, Pandas DataFrame 

	Take the pandas dataframe, and put all those data points in year year and any prior years into the training data.
	Also put all those months that are within months_forward past that year into the training data. For example, 
	if year is 2013 and months_foward is 3, take all data from year 2012 and 2013 and put that into the training 
	data. In addition, put the first 3 months of 2014 into the training data. Use the rest as the test data set.
	''' 

	df.loc[:, 'date_fire'] = pd.to_datetime(df['date_fire'].copy())
	# If we want more than 12 months forward, then we want a whole nother year, so let's just adjust the 
	# year and months_forward variables to handle that. 
	if months_forward >= 12 and year == True: 
		input_date_split += 1
		months_forward -= 12

	if year == True: 
		date_split = datetime.date(input_date_split + 1, 1, 1)
	else: 
		date_split = input_date_split

	date_split_forward = return_month_start(date_split, months_forward, forward = True)

	if months_backward: 
		date_split_backward = return_month_start(date_split_forward, months_backward, forward = False)
	else: 
		date_split_backward = df.date_fire.min()

	if days_forward: 
		date_split_forward2 = date_split_forward + datetime.timedelta(days=days_forward)
	else: 
		date_split_forward2 = df.date_fire.max()

	train = df.query('date_fire <= @date_split_forward and date_fire >= @date_split_backward')
	test = df.query('date_fire > @date_split_forward and date_fire <= @date_split_forward2')

	return train, test

def return_month_start(time, n_months, forward=True): 
	'''
	Input: datetime.date
	Output: datetime.date

	For the given datetime.date, return a datetime.date object that is the date for the first day in the 
	nth month ahead. For example, if I feed in January and the number 3, then I want this to spit back a 
	datetime.date that is the first day of the month of April in the same year.
	'''

	# Go ahead and move the inputted time forward at least 27 days for the number of months 
	# that we want. We know that there are at least 27 days in each month, and that this step will 
	# put us only a handful of days away from the start of the month we want. We can then step through 
	# day by day until the month changes. 

	month_operator = operator.add
	if forward == False: 
	    month_operator = operator.sub

	if n_months == 0: 
		return time

	time2 = month_operator(time, datetime.timedelta(days=(27 * n_months)))

	one_day = datetime.timedelta(days=1)
	date_to_return = month_operator(time2, one_day) 

	if forward == True: 
	    while date_to_return.month == time2.month: 
	        date_to_return += one_day
	else:
	    while date_to_return.day != time.day: 
	        date_to_return -= one_day

	return date_to_return 

def tt_split_same_months(df, year_split, month_split, exact_split_date = None, days_back = None):
	'''
	Input: Pandas DataFrame, Integer, List of Integers
	Output: Pandas DataFrame, Pandas DataFrame 

	For the inputted pandas dataframe and month put in, grab all months of
	data that are equal to the months in the month_split list, for any year. 
	For those that are in a year prior or equal to the inputted year, put 
	those in the training set, and for all others put them in the test set. 
	'''


	if exact_split_date is None: 
		if month_split[0] >= 13: 
			year_split += 1
			for idx, month in enumerate(month_split): 
				month_split[idx] -= 12

		df.loc[:, 'date_fire'] = pd.to_datetime(df['date_fire'].copy())
		df['year'] = [dt.year for dt in df['date_fire']]
		df['month'] = [dt.month for dt in df['date_fire']]

		train = df.query('year <= @year_split and month in @month_split') 
		test = df.query('year > @year_split and month in @month_split') 
	else:  
		exact_split_end = exact_split_date - datetime.timedelta(days=365)
		exact_split_start = exact_split_end - datetime.timedelta(days=days_back)
		train = df.query('date_fire >= @exact_split_start and date_fire <= @exact_split_end')
		# If we are passing in an exact date its for our hold out set, and so we don't 
		# have a test set (we just want to parse the training set a little farther). 
		test = pd.DataFrame()
		for years_back in xrange(2, 4): 
			exact_split_end = exact_split_date - datetime.timedelta(days = years_back * 365)
			exact_split_start = exact_split_end - datetime.timedelta(days=days_back)
			queried_df = df.query('date_fire >= @exact_split_start and date_fire <= @exact_split_end')
			train = train.append(queried_df)


	return train, test
