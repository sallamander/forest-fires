import pandas as pd
import pickle
import psycopg2
import time
import os
import sys

def boundary_merge(new_col_name, shapefile_table_name, detected_fires_table, label):
	'''
	Input: String, String, String
	Output: PSQL Data Table

	For a given column name and table that contains shape information, create a new column 
	in the detected_fires_table that is fed in that contains a true or false value for whether
	each detected fire in the detected_fires_table is within any shape boundary from the 
	shapefile_table_name. 

	Notes: The best way I could see to do this query was to create a new table, delete the old 
	table, and then rename the new. 
	'''
	conn = psycopg2.connect(dbname='forest_fires', user=os.environ['USER'])
	cursor = conn.cursor()

	print 'In boundary merge'

	if label: 
		query = create_label_query(cursor, new_col_name, shapefile_table_name, detected_fires_table)
	else: 
		query = create_bool_query(cursor, new_col_name, shapefile_table_name, detected_fires_table)

	print 'got Query'
	
	cursor.execute(query)

	print 'executed'

	conn.commit()
	conn.close()

def create_bool_query(cursor, new_col_name, shapefile_table_name, detected_fires_table): 
	'''
	Input: String, String, String
	Output: String 

	Take in the new column name to create, the table that holds the shapefile boundaries, 
	and the detected_fires_table, and write a query that will effectively create the 
	new column in the detected_fires_table, where the new column will hold true or false
	for whether the detected fire falls within any shape boundary from the 
	shapefile_table_name. 

	Notes: This might not be the cleanest way of doing this, but I spent some time 
	trying to use ALTER TABLE table update and/or INSERT INTO, and neither really panned out. 
	This works, and it's only being run a handful of times, so I'm not terribly worried at 
	this moment, but would like to know if there is a better way to do this. 
	'''

	delete_col_if_exists(cursor, [new_col_name], detected_fires_table)

	# If we are adding in a fire column, then we will be merging using the fire perimeter 
	# boundaries, which means we're merging on date and geometry. 
	on_query_part = 'ST_WITHIN(points.wkb_geometry, polys.wkb_geometry)'
	select_distinct_on = '(lat, long)'

	if new_col_name == 'fire_bool': 
		on_query_part += ' AND points.date = polys.date_'
		select_distinct_on = '(lat, long, date)'

	# The breakdown of this query ... kind of from the inside out.
	#  
	# 1.) Merge the detected fires data with whatever shapefile is inputted, and keep track 
	# 	of only the unique lat, long, date in a temporary table (called merged). 
	# 2.) Merge the detected fires data table with merged and along the way create a 
	#  	boolean that holds whether each row of the detected fire data table was within 
	# 	shape perimeter boundary. 
	# 3.) Create a new table holding these results. 
	query = '''CREATE TABLE {detected_fires_table}2 AS
				(WITH 
					distinct_to_merge AS 
						(SELECT DISTINCT ON {select_distinct_on} * 
						FROM {detected_fires_table}), 
					merged AS 
						(SELECT DISTINCT points.lat, points.long, points.date
						FROM distinct_to_merge as points
						INNER JOIN {shapefile_table_name} as polys
							ON {on_query_part})

				SELECT df.*, 
					CASE WHEN merged.lat IS NOT NULL THEN TRUE
						 WHEN merged.lat IS NULL THEN FALSE END AS {new_col_name}
				FROM {detected_fires_table} df
				LEFT JOIN merged 
					ON df.lat = merged.lat
					AND df.long = merged.long
					AND df.date = merged.date);'''.format(detected_fires_table=detected_fires_table, 
									shapefile_table_name=shapefile_table_name, 
									new_col_name=new_col_name, on_query_part=on_query_part, 
									select_distinct_on=select_distinct_on)
	return query

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

def create_label_query(cursor, new_col_name, shapefile_table_name, detected_fires_table): 
	'''
	Input: String, String, String
	Output: String

	Take in the new column name to create, the table that holds the shapefile boundaries, 
	and the detected_fires_table, and write a query that will effectively create the 
	new column in the detected_fires_table, where the new column will hold the label 
	for where the detected fire falls within that geometry. 

	Notes: This might not be the cleanest way of doing this, but I spent some time 
	trying to use ALTER TABLE table update and/or INSERT INTO, and neither really panned out. 
	This works, and it's only being run a handful of times, so I'm not terribly worried at 
	this moment, but would like to know if there is a better way to do this. 
	'''

	land, water, name, lsad= new_col_name + '_aland', new_col_name + '_water', new_col_name + '_name', new_col_name + '_lsad'
	columns_to_check = [land, water, name, lsad]
	polys_keep_columns = '''polys.aland as {land}, polys.awater as {water}, polys.name as {name}, 
						polys.lsad as {lsad}'''.format(land=land, water=water, name=name, lsad=lsad)
	if new_col_name == 'county': 
		polys_keep_columns += ', polys.countyfp as county_fips'
		columns_to_check.append('county_fips')
	if new_col_name == 'state': 
		polys_keep_columns += ', polys.statefp as state_fips'
		columns_to_check.append('state_fips')
	if new_col_name == 'region': 
		polys_keep_columns += ', polys.regionce as region_code'
		columns_to_check.append('region_code')

	delete_col_if_exists(cursor, columns_to_check, detected_fires_table)
							 
	query = '''CREATE TABLE {detected_fires_table}2 AS 
					(WITH 
						distinct_to_merge AS 
							(SELECT DISTINCT ON (lat, long) *
							FROM {detected_fires_table}), 
						merged AS 
							(SELECT DISTINCT points.lat, points.long, {polys_keep_columns}
							FROM distinct_to_merge as points
							INNER JOIN {shapefile_table_name} as polys
								ON ST_WITHIN(points.wkb_geometry, polys.wkb_geometry))

					SELECT df.*, {columns_to_check}
					FROM {detected_fires_table} df
					LEFT JOIN merged 
						ON df.lat = merged.lat
						AND df.long = merged.long
					);'''.format(detected_fires_table=detected_fires_table, 
								shapefile_table_name=shapefile_table_name, polys_keep_columns=polys_keep_columns, 
								columns_to_check=', '.join(columns_to_check))

	print 'query got it'

	return query

if __name__ == '__main__': 	
	if len(sys.argv) == 1: 
		with open('makefiles/year_list.pkl') as f: 
			year_list = pickle.load(f)
	elif len(sys.argv) == 2: 
		with open(sys.argv[1]) as f: 
			year_list = pickle.load(f)

	for year in [2012]: 
		detected_fires_table = 'detected_fires_' + str(year)
		# Start off with those shapefiles where we want a boolean if the detected fire is within that 
		# shape. 
		label = False
		# boundary_merge('fire_bool', 'perimeters_shapefiles_' + str(year), detected_fires_table, label)
		# If the year is equal to 2015, then we know the perimeter files aren't available yet (other than 
		# for detected fires, so we'll use the 2014 perimeter files). 
		if year == 2015: 
			year = 2014
		elif year == 2012: 
			year = 2013
		# boundary_merge('urban_area_bool', 'urban_shapefiles_' + str(year), detected_fires_table, label)

		# Now move to those shapefiles where we want labels/variables asscoiated with each detected point, because 
		# we know that they will fall into one of the shapes in each of these files (except for Canada). 
		label = True
		# boundary_merge('region', 'region_shapefiles_' + str(year), detected_fires_table, label)
		boundary_merge('county', 'county_shapefiles_' + str(year), detected_fires_table, label)
		# boundary_merge('state', 'state_shapefiles_' + str(year), detected_fires_table, label)