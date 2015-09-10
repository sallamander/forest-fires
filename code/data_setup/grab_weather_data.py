from requests import get
from pymongo import MongoClient
import pandas as pd
import multiprocessing
import sys
import pickle
import itertools
import numpy as np
import os 

def get_lat_long_time(year): 
	'''
	Input: Integer
	Output: Pandas DataFrame

	Read in the Pandas DataFrame for a given year, and grab the latitude, longitude, and 
	date to call the forecast.io with and get weather data. 
	'''
	df_filepath = '../../data/csvs/fires_' + str(year) + '.csv'

	df = pd.read_csv(df_filepath)

	return df[['lat', 'long', 'date']]

def get_unique_pairs(df, n, n_cores): 
	'''
	Input: Pandas DataFrame, Integer
	Output: Pandas DataFrame

	For the inputted data frame, take the unique lat, long, date pairs, go back n amount of days (i.e. 
	how many days back do we want weather), and then again get unique pairs (make sure that none of the days
	back that we went are overlapping). 
	'''
	col_names = df.columns
	df['date'] = pd.to_datetime(df['date'])

	# Grab the unique pairs of lat, long, date
	pairs_list = df.drop_duplicates().values
	pool = multiprocessing.Pool(processes=n_cores)

	# Map out the unique pairs of lat, long, date to multiple processes and spit back lat, long, date 
	# sets n days back. 
	outputs = np.array(pool.map(func=get_n_back, iterable=itertools.izip(pairs_list, itertools.repeat(n))))

	# Reshape the output to fit what we need. 
	n, m, p  = outputs.shape
	df = pd.DataFrame(data=outputs.reshape(n * m, p), columns=col_names)
	# Round the lat./long. coordinates to 2 decimal places, and drop duplicates. Rounding to .01 is 
	# roughly 1 km, which is a small village/town. It's hard to imagine that the weather differs
	# substantially across a small village/town. 
	df['lat'] = [np.round(lat, decimals=2) for lat in df['lat']]
	df['long'] = [np.round(long_coord, decimals=2) for long_coord in df['long']]

	return df.drop_duplicates()

def get_n_back(input_list): 
	'''
	Input: Set, Integer
	Output: Set

	Take the lat, long, date pairs set, and go back n days for each date, and then yield those lat, long date values. 
	'''
	row, n = input_list
	return [(row[0], row[1], row[2] - pd.Timedelta(days=day_back)) for day_back in xrange(0, n + 1)]

def store_unique_pairs(year, unique_pairs): 
	'''
	Input: Integer, Pandas Dataframe
	Output: CSV

	Read in the weater_{year} .csv file, and store the unique pairs of lat, long, date... but only if they 
	aren't already in that dataframe. I'm using this dataframe to make sure that I don't ever call the forecast.io
	api for the same lat, long, date pair. 
	'''
	weather_table = 'weather_' + str(year) + '.csv'
	weather_csv_path = '../../data/csvs/' + weather_table

	files = os.listdir('../../data/csvs/')

	if weather_table in files: 
		weather_df = pd.read_csv(weather_csv_path, parse_dates=[2])
		appended_weather_df, new_unique = add_unique_pairs(unique_pairs, weather_df)
		# If there are new unique lat, long, date combos to grab weather for, make sure 
		# we save a new .csv that holds those new ones (plus old ones), and then grab
		# the weather data for those. 
		if len(new_unique) > 0: 
			appended_weather_df.to_csv(weather_csv_path)
			new_unique = np.array(list(duplicated))
			new_unique_df = pd.DataFrame(data = duplicated_list)
			return new_unique_df
	else: 
		unique_pairs.to_csv(weather_csv_path, index=False)
		return unique_pairs

def add_unique_pairs(unique_pairs, weather_df): 
	'''
	Input: Pandas Dataframe, Pandas DataFrame
	Output: Pandas DataFrame, Set

	Add any new unique pairs to the weather_df to save (i.e. make sure we know we've gotten weather 
	data for these new lat, long, date pairs), and output the new_unique lat, long, date pairs 
	in a set so we can grab weather data for those. 
	'''
	unique_pairs['date'] = [pd.to_datetime(dt) for dt in unique_pairs['date'].values]
	weather_df = weather_df.append(unique_pairs)

	# Get the new unique lat, long, date pairs that we need weather data for. 
	new_set = set([(row[0], row[1], row[2]) for row in unique_pairs.values])
	current_set = set([(row[0], row[1], row[2]) for row in weather_df.values])
	new_unique = new_set - current_set

	return weather_df.drop_duplicates(), new_unique

def grab_weather_data(lat_long_date_df, year): 
	'''
	Input: Pandas DataFrame
	Output: Mongo Table

	For each of the lat, long, date pairs in the inputted DataFrame, call the forecast.io API and 
	get weather data for that date. 
	'''

	table = get_mongo_table(year)
	import pdb
	pdb.set_trace()
	r = lat_long_date_df.values[0]
	import pdb
	pdb.set_trace()

def make_forecast_io_call(row): 
	'''
	Input: NumpyArray
	Output: Results of forecast.io query. 
	'''
	forecast_io_key = os.environ['FORECAST_IO_KEY']
	lat_coord, long_coord, date = row 

	call_path = '''https://api.forecast.io/forecast/
				{api_key}/{lat},{long},{time}'''.format(api_key=forecast_io_key, 
				lat=lat_coord, long=long_coord, time=date)
	
def get_mongo_table(year): 
	'''
	Input: Integer
	Output: Mongo table instance
	'''

	table_name = 'weather_' + str(year)
	
	client = MongoClient()
	db = client['forest_fires']
	table = db[table_name]

	return table

if __name__ == '__main__': 
	if len(sys.argv) == 1: 
		with open('../makefiles/year_list.pkl') as f: 
			year_list = pickle.load(f)
	elif len(sys.argv) == 2: 
		with open(sys.argv[1]) as f: 
			year_list = pickle.load(f)

	year = 2013
	df = get_lat_long_time(year)
	unique_pairs = get_unique_pairs(df, 3, 2)
	new_pairs_to_grab = store_unique_pairs(year, unique_pairs)
	grab_weather_data(new_pairs_to_grab, year)
