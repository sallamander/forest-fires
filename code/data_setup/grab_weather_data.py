from requests import get
import psycopg2
import pandas as pd
import multiprocessing
import sys
import pickle

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

def get_unique_pairs(df, n): 
	'''
	Input: Pandas DataFrame, Integer
	Output: Pandas DataFrame

	For the inputted data frame, take the unique lat, long, date pairs, go back n amount of days (i.e. 
	how many days back do we want weather), and then again get unique pairs (make sure that none of the days
	back that we went are overlapping). 
	'''

	df['date'] = pd.to_datetime(df['date'])

	pairs_set = set([(row[0], row[1], row[2]) for row in df.values])
	pairs_set = set(get_n_back(pairs_set, n))

if __name__ == '__main__': 
	if len(sys.argv) == 1: 
		with open('../makefiles/year_list.pkl') as f: 
			year_list = pickle.load(f)
	elif len(sys.argv) == 2: 
		with open(sys.argv[1]) as f: 
			year_list = pickle.load(f)

	for year in year_list: 
		df = get_lat_long_time(year)
		get_unique_pairs(df, 3)
