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
	filepath = 'data/unzipped_files/detected_fires/MODIS/' + str(year)

	dt_name = 'detected_fires_' + str(year)
	create_db(filepath, dt_name)

def create_shapefile_db(name, year): 
	'''
	Input: String, Integer
	Output: PSQL Table

	For the given string name (county, fire, or urban), read in the shapefile for that geometry and create a 
	psql table from it. The county shapefile contains state labels as well, so that's why I'm not reading in 
	any state shapefiles. 
	'''
	latin_encoding = False

	if name == 'perimeters': 
		filepath = 'data/unzipped_files/boundary_files/fire_perimeters/' + str(year)
	elif name == 'county': 
		filepath = 'data/unzipped_files/boundary_files/county/' + str(year)
		latin_encoding = True
	elif name == 'urban': 
		latin_encoding = True
		filepath = 'data/unzipped_files/boundary_files/urban_areas/' + str(year)
	elif name == 'region': 
		latin_encoding = True
		filepath = 'data/unzipped_files/boundary_files/region/' + str(year)
	else: 
		raise Exception('No boundary folder name put in... Try again!')

	dt_name = name + '_shapefiles_' + str(year)
	create_db(filepath, dt_name, latin_encoding)

def create_db(filepath, dt_name, latin_encoding=False): 
	'''
	Input: String, String
	Output: PSQL Table

	Create a data table named dt_name in the forest_fires database from the shapefiles located in the folder 
	at filepath. 
	''' 

	if dt_exist(dt_name): 
		return 

	# I'm using the overwrite option here because anytime this I'm creating a db I'll be fixing something 
	# and need to create the database from scratch. Otherwise, I won't be running this function. 
	create_db_command = 'ogr2ogr -f "PostgreSQL" PG:"dbname=forest_fires user=' + os.environ['USER'] + \
						'"' + ' ' + filepath \
						+ ' -nlt PROMOTE_TO_MULTI -nln ' + dt_name + ' -overwrite'

	# Some of the shapefiles (county and urban area) need to be latin-encoded to read in correctly. 
	if latin_encoding:
		create_db_command = 'PGCLIENTENCODING=LATIN1 ogr2ogr -f "PostgreSQL" PG:"dbname=forest_fires user=' + os.environ['USER'] + \
					'"' + ' ' + filepath \
					+ ' -nlt PROMOTE_TO_MULTI -nln ' + dt_name + ' -overwrite'

	os.system(create_db_command)

def dt_exist(dt_name): 
	'''
	Input: String
	Output: Boolean 

	Take in the string of the datatable we are trying to create in the forest_fires 
	Database, test if that datatable already exists, and return a boolean for whether
	or not it does. 
	'''

	conn = psycopg2.connect(dbname='forest_fires')
	cursor = conn.cursor()

	try: 
		cursor.execute('SELECT * \
						FROM ' + dt_name + ' \
						LIMIT 1;')
	except: 
		return False

	return True 

if __name__ == '__main__': 
	with open(sys.argv[1]) as f: 
		year_list = pickle.load(f)
		
	for year in year_list: 
		create_fire_db(year)
		create_shapefile_db('perimeters', year)
		create_shapefile_db('county', year)
		create_shapefile_db('urban', year)
		create_shapefile_db('region', year)

		
