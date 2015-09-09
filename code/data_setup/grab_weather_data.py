from requests import get
import psycopg2
import pandas as pd
import multiprocessing

def get_lat_long_time(year): 
	'''
	Input: Integer
	Output: Pandas DataFrame

	Read in the Pandas DataFrame for a given year, and grab the latitude, longitude, and 
	date to call the forecast.io with and get weather data. 
	'''
	df_filepath = '../../data/csvs/fires_' + str(year)

	df = pd.read_csv(df_filepath)

	return df[['lat', 'long', 'date']]

def get_unique_pairs(df): 
	pass

if __name__ == '__main__': 
	if len(sys.argv) == 1: 
		with open('makefiles/year_list.pkl') as f: 
			year_list = pickle.load(f)
	elif len(sys.argv) == 2: 
		with open(sys.argv[1]) as f: 
			year_list = pickle.load(f)

	for year in year_list: 
		df = get_lat_long_time(year)
