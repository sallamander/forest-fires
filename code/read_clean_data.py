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
	Input: Integer, String
	Output: PSQL Table

	The basefile_name read in will point to a set of shapefiles. This function will read those shapefiles
	into a psql table. 
	'''
	filepath = '../../data/raw_data/MODIS/' + str(year) + '/' + basefile_name

	# I'm using the overwrite option here because anytime this create_fire_db step is run I'll be fixing something 
	# and need to create the database from scratch. Otherwise, I won't be running this function. 
	create_db_command = 'ogr2ogr -f "PostgreSQL" PG:"dbname=forest_fires user=' + os.environ['USER'] + \
						'" "/Users/' + os.environ['USER'] + '/galvanize/forest-fires/data/raw_data/MODIS/"' + str(year) \
						+ ' -nlt PROMOTE_TO_MULTI -nln fires_' + str(year) + ' -overwrite'
	
	os.system(create_db_command)

def create_shapefile_db(name, year): 
	'''
	Input: String, Integer
	Output: PSQL Table

	For the given string name (county, fire, or urban), read in the shapefile for that geometry and create a 
	psql table from it. The county shapefile contains state labels as well, so that's why I'm not reading in 
	any state shapefiles. 
	'''

	if name == 'fire': 
		filepath = '../../data/boundary_files/forest_fires/end_boundaries/' + str(year)
	elif name == 'county': 
		filepath = '../../data/boundary_files/county/' + str(year)
	elif name == 'urban': 
		filepath = '../../data/boundary_files/urban_areas' + str(year)
	else: 
		raise Exception('No boundary folder name put in... Try again!')

	create_db_command =  'ogr2ogr -f "PostgreSQL" PG:"dbname=forest_fires user=' + os.environ['USER'] + \
						'" "/Users/' + os.environ['USER'] + '/galvanize/forest-fires/data/raw_data/MODIS/"' + str(year) \
						+ ' -nlt PROMOTE_TO_MULTI -nln fires_' + str(year) + ' -overwrite'

	os.system(create_db_command)

def create_db(filepath, db_name): 
	'''
	Input: String, String
	Output: PSQL Table

	Create a data table named db_name in the forest_fires database from the shapefiles located in the folder 
	at filepath. 
	''' 

	create_db_command = 'ogr2ogr -f "PostgreSQL" PG:"dbname=forest_fires user=' + os.environ['USER'] + \
						'" "/Users/' + os.environ['USER'] + filepath \
						+ ' -nlt PROMOTE_TO_MULTI -nln ' + db_name + ' -overwrite'

	os.system(create_db_command)

def merge_fire_perimeters(year): 
	'''
	Input: Integer
	Output: PSQL Table

	Merge on the fire perimeters for the given year to that years table in the forest_fire database. 
	'''

	conn = psycopg2.connect('dbname=forest_fires')
	cursor = conn.cursor()

	cursor.execute('''CREATE TABLE forest_st_cnty AS
					 (SELECT points.*, polys.countyfp, polys.statefp
					 FROM forest_fires as points
							JOIN county as polys
					 ON ST_WITHIN(points.wkb_geometry, polys.wkb_geometry));
					''')


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

		
