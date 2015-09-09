def break_time_col(df, time_column): 
	'''
	Input: Pandas DataFrame, String
	Output: Pandas DataFrame

	The date/time column in our dataframe is in list format, where we have [YYYY, MM, DD]. 
	Here we're going to break that apart and create new variables in our dataframe. We'll delete
	the original data/time column after we're done. 
	'''

	time_col = df[time_column]
	df['year'] = [time[0] for time in time_col]
	df['month'] = [time[0] for time in time_col]
	df['day'] = [time[0] for time in time_col]

	# For now, I don't want to keep the day, just the year and month. 
	del df[[time_col, 'day']]