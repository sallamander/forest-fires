import pandas as pd
import numpy as np
import multiprocessing
from itertools import izip
from datetime import timedelta

def gen_nearby_fires_count(df, dist_measure, time_measures):
	'''
	Input: Pandas DataFrame, Float, List
	Output:  Pandas DataFrame

	For each row in the detected fires data set, create a new column that is the count of nearby 
	potential detected fires, where nearby detected fires are determined by the inputted dist_measure
	and time_measures list.  
	'''
	for time_measure in time_measures: 
		query_prep_clean(df, dist_measure, time_measure, beginning = True) 
		pool = multiprocessing.Pool(multiprocessing.cpu_count())
		nearby_count_dict = pool.map(query_for_nearby_fires, df2.values) 
		nearby_count_df = pd.DataFrame(nearby_count_dict)
		df = merge_results(df, nearby_count_df)
		query_prep_clean(df, dist_measure, time_measure, beginning=False)

	return df

def query_for_nearby_fires(row): 
	'''
	Input: Pandas DataFrame, Numpy Array, Float, Integer
	Output: Float

	For the inputted row, query the dataframe for the number of 'detected fires' (i.e. other rows) that 
	are within dist_measure of the inputted row and within the time_measure of the inputted row. 
	'''
	lat, lng, date = row[lat_idx], row[lng_idx], row[dt_idx]
	lat_min, lat_max = lat - dist_measure2, lat + dist_measure2
	long_min, long_max = lng - dist_measure2, lng + dist_measure2
	# Note we're not doing day_max here because in real time we wouldn't have forward dates. 
	date_min  = date - timedelta(days=time_measure2)
	query = '''lat >= @lat_min and lat <= @lat_max and long >= @long_min and long <= @long_max and date_temp >= @date_min and date_temp <= @date'''
	nearby_count = df2.query(query).shape[0]

	nearby_count_label = 'nearby_count_' + str(time_measure2)	
	output_dict = {'lat': lat, 'long': lng, 'date_count': date, nearby_count_label: nearby_count}
	return output_dict

def query_prep_clean(df, dist_measure, time_measure, beginning=True): 
	'''
	Input: Pandas DataFrame, Float, Float, Boolean
	Output: Global Variables (deleted or created)

	For the inputted dataframe and time dist measure, create the necessary global variables for 
	the multiprocessing environment. Since I am multiprocessing a dataframe query, I need to be able to 
	either pass the dataframe through the multiprocessing pool, or make it a global. While neither
	is ideal, the second seems better. I'll make sure to delete the global when I'm all done. 
	'''
	if beginning == True: 
		global df2, lat_idx, lng_idx, dt_idx, dist_measure2, time_measure2
		dist_measure2, time_measure2 = dist_measure, time_measure
		df2 = df.copy()
		df2['date_temp'] = pd.to_datetime(df2['date_fire'])
		df2 = add_hour_second(df2, 'date_temp')
		df_columns = df2.columns
		lat_idx, lng_idx, dt_idx = np.where(df_columns == 'lat')[0][0], np.where(df_columns == 'long')[0][0], np.where(df_columns == 'date_temp')[0][0] 
	if beginning == False:
		del df2, lat_idx, lng_idx, dt_idx, dist_measure2, time_measure2	

def merge_results(df, nearby_fires_df): 
	'''
	Input: Pandas DataFrame, Pandas DataFrame
	Output Pandas DataFrame

	Take in the nearby_fires_count_df, and merge it into the current df we are working with 
	to run it through the model. We will be merging by lat, long, and date
	'''
	df['date_count'] = pd.to_datetime(df['date_fire'])
	df = add_hour_second(df, 'date_count')
	nearby_fires_df = nearby_fires_df.drop_duplicates()
	df = pd.merge(df, nearby_fires_df, how='left', on=['lat', 'long', 'date_count'])
	df.drop('date_count', axis=1, inplace=True)

	return df

def add_hour_second(df, date_col_to_add_to): 
	'''
	Input: Pandas DataFrame 
	Output: Pandas DataFrame

	Take in the data frame, and add to the date_temp the hours and seconds so that we can make sure to only grab 
	those fires that are less than in time (where less than includes hours and seconds and not just the day). 
	'''
	
	hour = []
	minute = []
	for gmt in df.gmt.values:
		gmt = str(gmt)
		if len(gmt) == 3: 
			hour.append(int(gmt[0]))
			minute.append(int(gmt[1:]))
		else: 
			hour.append(int(gmt[0:2]))
			minute.append(int(gmt[2:]))

	df['hour'] = hour
	df['minute'] = minute
	df[date_col_to_add_to] = [date_temp + pd.Timedelta(hours=hour) + pd.Timedelta(minutes=minute) for date_temp, hour, minute in \
			  izip(df[date_col_to_add_to], df.hour, df.minute)]

	return df 
