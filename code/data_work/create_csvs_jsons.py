import psycopg2
import os
import json 
import pandas as pd

def output_csv(year): 
	'''
	Input: Intger
	Output: CSV file

	Ouptut the postgres detected_fires table for the inputted year into a .csv. 
	'''

	check_create_dir('csvs')

	conn = psycopg2.connect(dbname='forest_fires', user=os.environ['USER'], host='localhost')
	cursor = conn.cursor()

	filename = 'fires_' + str(year) + '.csv'
	filepath = get_filepath(filename)

	print filepath

	cursor.execute('''COPY detected_fires_{year} to 
				'{filepath}' DELIMITER AS ',' 
				CSV HEADER;'''.format(filepath=filepath, year=str(year)))

	conn.commit()
	conn.close()

def output_json(year, geo_type):
	'''
	Input: Integer, String
	Output: JSON File

	For the given year and geography type, create JSON files that hold the geoJSON for mapping 
	that geography type. 
	'''
 		
 	query = get_json_query(geo_type, year)

 	df = pd.read_sql(map_query, conn)

	list_to_export = []	
	for idx, row in df.iterrows():
		list_to_export.append((add_properties_geo(row, geo_type)))

	filename = year + '_' + geo_type + '.json'
	json = True
	filepath = get_filepath(filename, json)
	with open(filepath, 'w+') as f: 
		f.write(json.dumps(list_to_export))

def get_json_query(geo_type, year): 
	'''
	Input: String 
	Output: String

	For the given geotype, output a query string to pull properties from its table so that we can create a 
	geojson file. 
	'''

	from_table = geo_type + '_shapefiles_' + str(year)
	select_variables = ' ST_asGeoJSON(wkb_geometry) as geometry, name, '

	if geo_type == 'state': 
		select_variables += 'statefp'
	elif geo_type == 'county':
		select_variables += 'statefp, countyfp, state_name'
	elif geo_type == 'region': 
		select_variables += 'regionce'


	query = '''SELECT {select_variables} 
				FROM {from_table};
			'''.format(select_variables=select_variables, from_table=from_table)

def add_properties_geo(row, geo_type):
	properties_dict = {}
	properties_dict['name'] = row['name']
	if geo_type == 'state': 
		properties_dict['state_fips'] = row['statefp']
	elif geo_type == 'county': 
		properties_dict ['state_fips'] = row['statefp']
		properties_dict['county_fips'] = row['countyfp']
		properties_dict['state_name'] = row['state_name']
	elif geo_type == 'region': 
		properties_dict['region_number'] = row['regionce']

	geo_json = {"type": "Feature", "geometry": json.loads(row['geometry']),  "properties": properties_dict} 
	return geo_json


def check_create_dir(data_dir_name): 
	'''
	Input: None
	Output: Possibly Created Directory/Folder

	Check to make sure the data/data_dir_name directory/folder is created, and if not create it. 
	'''

	# In the hopes of generalizing this so I can easily throw it up on AWS or somebody else can 
	# use it, I'm going to find the current directory path, remove any directories /forest-fires
	# and deeper, and then create the data_dir_name in forest-fires/data/data_dir_name. This is to make
	# sure that this works no matter where the file is run from. 
	current_dir = os.getcwd()
	location = current_dir.find('forest-fires')

	if location == -1: 
		smokey_error()
	else: 
		data_dirs = os.listdir(current_dir[:location] + '/forest-fires/data/')
		if data_dir_name not in data_dirs: 
			os.mkdir(current_dir[:location] + '/forest-fires/data/' + data_dir_name)

def get_filepath(filename): 
	'''
	Input: String
	Output: String 

	Take in the given filename, and output the filepath to save it. The reason this is in a function 
	is to again help generalize in the case that somebody else wants to use it or I throw it up on AWS. 
	This will make sure that the filename gets saved in the /data/jsons folder, regardless of what folder
	this program is run from (unless it's outside the forest-fires folder). 
	'''
	current_dir = os.getcwd()
	location = current_dir.find('forest-fires')

	if location == -1: 
		smokey_error()
	else: 
		if filename.find('.json') != -1: 
			return current_dir[:location] + 'forest-fires/data/jsons/' + filename
		elif filename.find('.csv') != -1: 
			return current_dir[:location] + 'forest-fires/data/csvs/' + filename

def smokey_error(): 
	'''
	Input: None
	Output: Raised Error
	'''
	raise Exception("You're not running this code from anywhere in you're forest-fire directory... \
				Smokey would be ashamed!")

if __name__ == '__main__': 
	for year in xrange(2013, 2015): 
		# output_csv(year)
		output_json(year, 'state')

