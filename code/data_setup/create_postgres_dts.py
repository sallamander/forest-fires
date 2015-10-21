import pickle
import sys
import psycopg2
import os
import pandas as pd

def create_fire_db(year): 
	'''
	Input: Integer 
	Output: PSQL Table 
        
        For the given year, generate two strings, one that holds the filepath 
        to where the unzipped detected fires dataset for that year is being 
        held, and the other that holds what the data table will be named in 
        postgres. Input those two strings into the create_dt function, 
        which will actually create the data table in our forest_fires postgres
        data base. 
	'''

	filepath = '../data/unzipped_files/detected_fires/MODIS/' + str(year)

	dt_name = 'detected_fires_' + str(year)
	create_dt(filepath, dt_name)

def create_shapefile_db(name, year, latin_encoding=False): 
	'''
	Input: String, Integer, Boolean
	Output: PSQL Table

        For the given year, generate two strings, one that holds the filepath 
        to where the unzipped shapefile dataset for that year is being 
        held, and the other that holds what the data table will be named in 
        postgres. Input those two strings into the create_dt function, 
        which will actually create the data table in our forest_fires postgres
        data base. 
	'''

	if name == 'perimeters': 
		filepath = '../data/unzipped_files/boundary_files/fire_perimeters/' + str(year)
	elif name == 'county': 
		filepath = '../data/unzipped_files/boundary_files/county/' + str(year)
	elif name == 'urban': 
		filepath = '../data/unzipped_files/boundary_files/urban_areas/' + str(year)
	elif name == 'region': 
		filepath = '../data/unzipped_files/boundary_files/region/' + str(year)
	elif name == 'state': 
		filepath = '../data/unzipped_files/boundary_files/state/' + str(year)
	else: 
		raise Exception('No boundary folder name put in... Try again!')

	dt_name = name + '_shapefiles_' + str(year)
	create_dt(filepath, dt_name, latin_encoding)

def create_dt(filepath, dt_name, latin_encoding=False): 
	'''
	Input: String, String, Boolean
	Output: PSQL Table

	Create a data table named dt_name in the forest_fires database from the 
        shapefiles located in the folder at filepath. The latin_encoding boolean 
        makes sure to adjust the way the data is encoded when being read in. 
        For a couple of the shapefiles, it allows the data to be read in properly. 
	''' 

        # Issue a warning and abort if table already exists.
        if dt_exists(dt_name): 
            raise Exception('This table already exists!)

	# I'm using the overwrite option here because anytime this I'm creating a 
        # db I'll be fixing something and need to create the database from scratch. 
        # Otherwise, I won't be running this function. 

	if latin_encoding:
		create_dt_command = 'PGCLIENTENCODING=LATIN1 ogr2ogr -f "PostgreSQL" ' + \
                                    'PG:"dbname=forest_fires user=' + os.environ['USER'] + \
				    '"' + ' ' + filepath + ' -nlt PROMOTE_TO_MULTI -nln ' \
                                    + dt_name + ' -overwrite'
        else: 
	    create_dt_command = 'ogr2ogr -f "PostgreSQL" PG:"dbname=forest_fires ' + \
                                'user=' + os.environ['USER'] + '"' + ' ' + filepath \
			        + ' -nlt PROMOTE_TO_MULTI -nln ' + dt_name + ' -overwrite'

	os.system(create_dt_command)

def dt_exist(dt_name): 
	'''
	Input: String
	Output: Boolean 

	Take in the string of the datatable we are trying to create in the forest_fires 
	database, test if that datatable already exists, and return a boolean for whether
	or not it does. 
	'''

	conn = psycopg2.connect(dbname='forest_fires', user=os.environ['USER'])
	cursor = conn.cursor()

	try: 
		cursor.execute('SELECT * FROM ' + dt_name + ' LIMIT 1;')
	except: 
		return False

	return True 

if __name__ == '__main__': 
    for year in xrange(2012, 2016): 
        create_fire_db(year)
        create_shapefile_db('perimeters', year)

        # We only have the following perimter shapefiles for 2013 and 2014. 
        if year not in (2012, 2015): 
            create_shapefile_db('county', year, latin_encoding=True)
            create_shapefile_db('state', year)
            create_shapefile_db('urban', year, latin_encoding=True)
            create_shapefile_db('region', year, latin_encoding=True)
            
        
