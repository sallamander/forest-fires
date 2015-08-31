import shapefile
import pandas as pd
import numpy as np
import pickle
import sys
import psycopg2
import os
from collections import defaultdict

def create_fire_db(year, basefile_name): 
	'''
	Input: String
	Output: Pandas DataFrame

	Read in the shapefiles from the given filepath and translate the result into a 
	pandas dataframe. 
	'''
	filepath = '../../data/raw_data/MODIS/' + str(year) + '/' + basefile_name

	create_db_command = 'ogr2ogr -f "PostgreSQL" PG:"dbname=forest_fires user=' + os.environ['user'] + \
						'" "/Users/' + os.environ['user'] + '/galvanize/forest-fires/data/raw_data/MODIS/2014" \
						-nlt PROMOTE_TO_MULTI -nln forest_fires'
	
	os.system(create_db_command)

def get_basefile_name(year): 
	'''
	Input: Integer
	Output: String

	Take in the given year, navigate to the satellite data for that year, and 
	pull the basefile name that the shapefile library will need to put all 
	of the files together. 
	'''
	current_dir = '../../data/raw_data/MODIS/' + str(year) + '/'
	files = os.listdir(current_dir)

	ext_index = files[0].find('.')
	basefile_name = files[0][:ext_index]
	return basefile_name

def format_df(df): 
	'''
	Input: Pandas DataFrame
	Output: Pandas DataFrame

	In the years 2008 and prior, the data is formatted slightly differently than later years. The 
	Fire_ and Fire_ID variables from later years are named differently, as are the LAT and LONG 
	variables. For these, we simply need to change names. For the TEMP variable from years 2009+, we need to 
	use the T21 from the years prior to 2008, and for the JULIAN varible in years 2009+, we need to parse
	part of the JDATE variable. 
	'''

	df = df.rename(columns={'MCD14ML_': 'FIRE_', 'MCD14ML_ID': 'FIRE_ID', 'WGS84LAT': 'LAT', 'WGS84LONG': 'LONG', 
							'T21': 'TEMP', 'UTC': 'GMT', 'SATELLITE': 'SAT_SRC', 'CONFIDENCE': 'CONF'})
	df['JULIAN'] = df['JDATE'].apply(lambda x: int(str(x)[-3:]))
	df = df.drop(['T31', 'JDATE'], axis=1)

	return df

def pickle_df_sf(year, df): 
	'''
	Input: Integer, Pandas DataFrame
	Ouput: Pickled file of DataFrame
	'''

	with open('../../data/pickled_data/MODIS/' + 'df_' + str(year) + '.pkl', 'w+') as f: 
		pickle.dump(df, f)

if __name__ == '__main__': 
	year = sys.argv[1]	
	basefile_name = get_basefile_name(year)
	create_fire_db(year, basefile_name)
	# pickle_df_sf(year, shapefile_df)

		
