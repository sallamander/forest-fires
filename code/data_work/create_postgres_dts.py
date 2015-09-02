import pickle
import sys
import psycopg2
import os
import pandas as pd

def create_fire_db(year): 
	'''
	Input: Integer, String
	Output: PSQL Table

	The basefile_name read in will point to a set of shapefiles. This function will read those shapefiles
	into a psql table. 
	'''
	filepath = '../data/raw_data/MODIS/' + str(year)

	db_name = 'detected_fires_' + str(year)
	create_db(filepath, db_name)

def create_shapefile_db(name, year): 
	'''
	Input: String, Integer
	Output: PSQL Table

	For the given string name (county, fire, or urban), read in the shapefile for that geometry and create a 
	psql table from it. The county shapefile contains state labels as well, so that's why I'm not reading in 
	any state shapefiles. 
	'''
	latin_encoding = False

	if name == 'end_fire': 
		filepath = '../data/boundary_files/forest_fires/end_boundaries/' + str(year)	
	elif name == 'daily_fire': 
		filepath = '../data/boundary_files/forest_fires/daily_boundaries/' + str(year)
	elif name == 'county': 
		filepath = '../data/boundary_files/county/' + str(year)
		latin_encoding = True
	elif name == 'urban': 
		latin_encoding = True
		filepath = '../data/boundary_files/urban_areas/' + str(year)
	else: 
		raise Exception('No boundary folder name put in... Try again!')

	db_name = name + '_shapefiles_' + str(year)
	create_db(filepath, db_name, latin_encoding)

def create_db(filepath, db_name, latin_encoding=False): 
	'''
	Input: String, String
	Output: PSQL Table

	Create a data table named db_name in the forest_fires database from the shapefiles located in the folder 
	at filepath. 
	''' 

	if db_exist(db_name): 
		return 

	# I'm using the overwrite option here because anytime this I'm creating a db I'll be fixing something 
	# and need to create the database from scratch. Otherwise, I won't be running this function. 
	create_db_command = 'ogr2ogr -f "PostgreSQL" PG:"dbname=forest_fires user=' + os.environ['USER'] + \
						'"' + ' ' + filepath \
						+ ' -nlt PROMOTE_TO_MULTI -nln ' + db_name + ' -overwrite'

	# Some of the shapefiles (county and urban area) need to be latin-encoded to read in correctly. 
	if latin_encoding:
		create_db_command = 'PGCLIENTENCODING=LATIN1 ogr2ogr -f "PostgreSQL" PG:"dbname=forest_fires user=' + os.environ['USER'] + \
					'"' + ' ' + filepath \
					+ ' -nlt PROMOTE_TO_MULTI -nln ' + db_name + ' -overwrite'

	os.system(create_db_command)

def db_exist(db_name): 
	'''
	Input: String
	Output: Boolean 

	Take in the string of the datatable we are trying to create in the forest_fires 
	Database, test if that datatable already exists, and return a boolean for whether
	or not it does. 
	'''

	conn = psycopg2.conn(dbname='forest_fires')
	cursor = conn.cursor()

	cursor.execute('SELECT * \
					FROM ' + db_name + ' \
					LIMIT 1;')

	if cursor.fetchall(): 
		return True 
	else: 
		return False




if __name__ == '__main__': 
	with open(sys.argv[1]) as f: 
		year_list = pickle.load(f)
		
	for year in year_list: 
		create_fire_db(year)
		create_shapefile_db('end_fire', year)
		create_shapefile_db('daily_fire', year)
		create_shapefile_db('county', year)
		create_shapefile_db('urban', year)

		
