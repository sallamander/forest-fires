import psycopg2
import os
import sys
import pickle

def add_stname_county(year): 
	'''
	Input: Integer
	Output: Updated DataTable

	Merge on the state name to the county_shapefiles table, so that we have the state name associated
	with each county, and not just the state fips. 
	'''

	conn = psycopg2.connect(dbname='forest_fires', user=os.environ['USER'], host='localhost')
	cursor = conn.cursor()

	county_table = 'county_shapefiles_' + str(year)
	state_table = 'state_shapefiles_' + str(year)

	delete_col_if_exists(cursor, ['state_name'], county_table )
	
	cursor.execute(''' CREATE TABLE {county_table}2 AS 
							(SELECT st.name as state_name, ct.* 
							FROM {county_table} ct 
							INNER JOIN {state_table} st 
								ON ct.statefp = st.statefp)
					;'''.format(county_table=county_table, state_table=state_table))


	cursor.execute(''' DROP TABLE {}'''.format(county_table))
	cursor.execute(''' ALTER TABLE {county_table}2 
						RENAME TO {county_table}'''.format(county_table=county_table))

	conn.commit()
	conn.close()

def rename_urban_name(year):
	'''
	Input: Integer
	Output: Updated Datatable

	Rename the name10 column in the urban shapefiles tables so that it matches the other tables. 
	'''

	conn = psycopg2.connect(dbname='forest_fires', user=os.environ['USER'], host='localhost')
	cursor = conn.cursor()

	urban_table = 'urban_shapefiles_' + str(year)
	if name_10(cursor, urban_table): 
		cursor.execute(''' ALTER TABLE {urban_table} RENAME COLUMN name10 TO name;'''.format(urban_table=urban_table))

	conn.commit()
	conn.close()

def delete_col_if_exists(cursor, cols_list, detected_fires_table): 
	'''
	Input: Pyscopg2 cursor, String, String, String
	Output: None

	Delete the new column that we want to insert from the detected fires table if it already 
	exists. 
	'''

	for col in cols_list: 
		cursor.execute('''ALTER TABLE {detected_fires_table}
						DROP COLUMN IF EXISTS {new_col_name};
					'''.format(detected_fires_table=detected_fires_table, 
								new_col_name=col))

def name_10(cursor, urban_table): 
	'''
	Input: psycopg2 cursor, String
	Output: Boolean

	Check if the name10 column exists in the urban_table, so we know if we can rename it (can't rename it 
	if it doesn't exist). 
	'''

	cursor.execute(''' SELECT column_name 
						FROM information_schema.columns 
						WHERE table_name='{urban_table}' 
							AND column_name='name10';'''.format(urban_table=urban_table))
	result = cursor.fetchall()
	if len(result) == 0: 
		return False
	else: 
		return True	


if __name__ == '__main__': 
	if len(sys.argv) == 1: 
		with open('makefiles/year_list.pkl') as f: 
			year_list = pickle.load(f)
	elif len(sys.argv) == 2: 
		with open(sys.argv[1]) as f: 
			year_list = pickle.load(f)

	for year in year_list: 
		if year != 2015: 
			add_stname_county(year)
			rename_urban_name(year)


 

