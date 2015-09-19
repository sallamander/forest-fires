import pandas as pd
from datetime import timedelta

def gen_nearby_fires_count(df, dist_measure, time_measure):
	'''
	Input: Pandas DataFrame, Float, Integer
	Output:  Pandas DataFrame

	For each row in the detected fires data set, create a new column that is the count of nearby 
	potential detected fires, where nearby detected fires are determined by the inputted dist_measure
	and time_measure. 
	'''
	df['date_temp'] = pd.to_datetime(df['date_fire'])
	df['nearby_fires'] = [query_for_nearby_fires(df, row, dist_measure, time_measure) for row in df.values]
	df.drop('date_temp', axis=1, inplace=True)
	import pdb
	pdb.set_trace()
	return df

def query_for_nearby_fires(df, row, dist_measure, time_measure): 
	'''
	Input: Pandas DataFrame, Numpy Array, Float, Integer
	Output: Float

	For the inputted row, query the dataframe for the number of 'detected fires' (i.e. other rows) that 
	are within dist_measure of the inputted row and within the time_measure of the inputted row. 
	'''
	lat, lng, date = df['lat'], df['long'], df['date_temp']
	lat_min, lat_max = lat - dist_measure, lat + dist_measure
	long_min, long_max = lng - dist_measure, lng + dist_measure
	# Note we're not doing day_max here because in real time we wouldn't have forward dates. 
	date_min  = date - timedelta(days=time_measure)

	query = 'lat >= @lat_min and lat <= @lat_max and long >= @long_min and long <= @long_max and date_temp >= @date_min'
	nearby_count = df.query(query).count()

	return nearby_count
	
