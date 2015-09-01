import pickle
import sys
import psycopg2
import os

def create_fire_db(year): 
	'''
	Input: Integer, String
	Output: PSQL Table

	The basefile_name read in will point to a set of shapefiles. This function will read those shapefiles
	into a psql table. 
	'''
	filepath = '../../data/raw_data/MODIS/' + str(year)

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

	if name == 'fire': 
		filepath = '../../data/boundary_files/forest_fires/end_boundaries/' + str(year)
	elif name == 'county': 
		filepath = '../../data/boundary_files/county/' + str(year)
		latin_encoding = True
	elif name == 'urban': 
		latin_encoding = True
		filepath = '../../data/boundary_files/urban_areas/' + str(year)
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
	create_fire_db(year)
	create_shapefile_db('fire', year)
	create_shapefile_db('county', year)
	create_shapefile_db('urban', year)
	# pickle_df_sf(year, shapefile_df)

		
