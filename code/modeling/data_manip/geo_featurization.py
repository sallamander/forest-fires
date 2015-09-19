import pandas as pd

def gen_nearby_fires_count(df, dist_measure, time_measure):
	'''
	Input: Pandas DataFrame, Float, Integer
	Output:  Pandas DataFrame

	For each row in the detected fires data set, create a new column that is the count of nearby 
	potential detected fires, where nearby detected fires are determined by the inputted dist_measure
	and time_measure. 
	'''

	df['nearby_fires'] = [query_for_nearby_fires(df, row, dist_measure, time_measure) for row in df.values]

def query_for_nearby_fires(df, row, dist_measure, time_measure): 
	'''
	Input: Pandas DataFrame, Numpy Array, Float, Integer
	Output: Float

	For the inputted row, query the dataframe for the number of 'detected fires' (i.e. other rows) that 
	are within dist_measure of the inputted row and within the time_measure of the inputted row. 
	'''

	lat, lng, date = df['lat'], df['long'], df['fire_date']
	lat_min, lat_max = lat - dist_measure, lat + dist_measure
	long_min, long_max = lng - dist_measure, lng + dist_measure
	# Note we're not doing day_max here because in real time we wouldn't have forward dates. 
	date_min  = date - pd.TimeDelta(days=time_measure)

	query = ''' latitude >= @lat_min and latitude <= @lat_max and longitude >= @long_min and 
				longitude <= @long_max and date >= date_min
			'''
	nearby_count = df.query(query).count()

	return nearby_count
	
