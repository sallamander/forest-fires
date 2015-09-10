from requests import get
import psycopg2
import pandas as pd
import multiprocessing
import sys
import pickle
import itertools
import numpy as np
import os
from create_postgres_dts import dt_exist

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

	return df.drop_duplicates()

def get_n_back(input_list): 
	'''
	Input: Set, Integer
	Output: Set

	Take the lat, long, date pairs set, and go back n days for each date, and then yield those lat, long date values. 
	'''
	row, n = input_list
	return [(row[0], row[1], row[2] - pd.Timedelta(days=day_back)) for day_back in xrange(0, n + 1)]

def create_weather_dt(year): 
	'''
	Input: Integer
	Output: Potentially Created Datatable. 

	For the given year, create the weather_{year} data table in the forest_fires database if it isn't already created. 
	'''

	conn = psycopg2.connect(dbname='forest_fires', user=os.environ['USER'])
	cursor = conn.cursor()

	dt_name = 'weather_' + str(year)

	if dt_exist(dt_name): 
		pass
	else: 
		cursor.execute('''CREATE TABLE weather_{year} (
						    lat         float NOT NULL,
						    long		float NOT NULL,
						    date 		date NOT NULL
						);'''.format(year=year))

	conn.commit()
	conn.close()

def input_unique_pairs(year, unique_pairs):
	pass 

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
	create_weather_dt(year)
