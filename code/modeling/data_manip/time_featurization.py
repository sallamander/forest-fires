def break_time_col(df, time_column): 
	'''
	Input: Pandas DataFrame, String
	Output: Pandas DataFrame

	The date/time column in our dataframe is in list format, where we have [YYYY, MM, DD]. 
	Here we're going to break that apart and create new variables in our dataframe. We'll delete
	the original data/time column after we're done. 
	'''

	time_col = df[time_column]
	df['year'] = [time[0:4] for time in time_col]
	df['month'] = [time[5:7] for time in time_col]

	return df