import pandas as pd
import pickle
import psycopg2
import time
import os
import sys

def boundary_merge(boundary_type, shapefile_table_name, detected_fires_table, label):
	'''
	Input: String, String, String, Boolean
	Output: PSQL Data Table

        For the given boundary type, generate a query (using create_label_query)
        that will join the shapefile_table_name with the detected_fires_table, 
        either generating a boolean for whether the lat/long of each detected
        fire fell within that boundary (label = False), or a label for information
        of where within that boundary type the detected fire fell (i.e. state info, 
        county info, etc.). Then, execute the query. 
	'''

	conn = psycopg2.connect(dbname='forest_fires', user=os.environ['USER'])
	cursor = conn.cursor()

	if label: 
		query = create_label_query(cursor, boundary_type, shapefile_table_name, 
                        detected_fires_table)
	else: 
		query = create_bool_query(cursor, boundary_type, shapefile_table_name, 
                        detected_fires_table)

	cursor.execute(query)

	conn.commit()
	conn.close()

def create_bool_query(cursor, boundary_type, shapefile_table_name, detected_fires_table): 
	'''
	Input: PyscoPg2 Cursor Object, String, String, String
	Output: String 

	Take in the cursor object (allows us to delete a column named boundary_type if 
        it already exists in the detected_fires_table), the table name that holds the
        shapefile boundaries, and the table name detected_fires_table, and write a 
        query that will effectively create the boundary_type column in the 
        detected_fires_table, where the boundary_type column will hold true or false
	for whether the detected fire falls within any shape boundary from the 
	shapefile_table_name. 

	Notes: This might not be the cleanest way of doing this, but I spent some time 
	trying to use ALTER TABLE table update and/or INSERT INTO, and neither really panned out. 
	This works, and it's only being run a handful of times, so I'm not terribly worried at 
	this moment, but would like to know if there is a better way to do this. 
	'''

	delete_col_if_exists(cursor, [boundary_type], detected_fires_table)

	# If we are adding in a fire column, then we will be merging using the fire perimeter 
	# boundaries, which means we're merging on date and geometry. 
	on_query_part = 'ST_WITHIN(points.wkb_geometry, polys.wkb_geometry)'
	select_distinct_on = '(lat, long)'

	if boundary_type == 'fire_bool': 
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
						 WHEN merged.lat IS NULL THEN FALSE END AS {boundary_type}
				FROM {detected_fires_table} df
				LEFT JOIN merged 
					ON df.lat = merged.lat
					AND df.long = merged.long
					AND df.date = merged.date);'''.format(detected_fires_table=detected_fires_table, 
									shapefile_table_name=shapefile_table_name, 
									boundary_type=boundary_type, on_query_part=on_query_part, 
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
						DROP COLUMN IF EXISTS {boundary_type};
					'''.format(detected_fires_table=detected_fires_table, 
								boundary_type=col))

def create_label_query(cursor, boundary_type, shapefile_table_name, detected_fires_table): 
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

	land, water, name, lsad= boundary_type + '_aland', boundary_type + '_water', boundary_type + '_name', boundary_type + '_lsad'
	columns_to_check = [land, water, name, lsad]
	polys_keep_columns = '''polys.aland as {land}, polys.awater as {water}, polys.name as {name}, 
						polys.lsad as {lsad}'''.format(land=land, water=water, name=name, lsad=lsad)
	if boundary_type == 'county': 
		polys_keep_columns += ', polys.countyfp as county_fips'
		columns_to_check.append('county_fips')
	if boundary_type == 'state': 
		polys_keep_columns += ', polys.statefp as state_fips'
		columns_to_check.append('state_fips')
	if boundary_type == 'region': 
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
        ''' 
        For the fire perimeter boundaries, along with county, state, urban area, and 
        region boundaries, we want to know if our detected fire (i.e. its lat/long
        coordinates) fall within those boundaries. For some of these (fire 
        perimeter, urban area), we just want a boolean of whether or not it 
        fell within those boundaries. For the others (county, state, region), 
        we want to know what county/state/region it fell in, along with some of 
        the other information that is available with those geographies. 

        To figure this out, we will take advantage of the POSTGIS extension, 
        which will allow us to join two tables, asking whether or not the geography 
        from one table (lat/long coordinates) fall within another geography 
        (a perimeter boundary).
        '''

	for year in xrange(2012, 2016): 
		detected_fires_table = 'detected_fires_' + str(year)
		# Start off with those shapefiles where we simply want a boolean if 
                # the detected fire is within that shape. 

		label = False
		boundary_merge('fire_bool', 'perimeters_shapefiles_' + str(year), 
                                detected_fires_table, label)

                # The state, county, urban area, and region shapefiles aren't 
                # available for 2012 or 2015. We'll resort to using the 
                # closest year.
		if year == 2015: 
			year = 2014
		elif year == 2012: 
			year = 2013

		boundary_merge('urban_area_bool', 'urban_shapefiles_' + str(year), 
                                detected_fires_table, label)

		# Now move to those shapefiles where we want labels/variables asscoiated 
                # with each detected point, because we know that they will fall into one 
                # of the shapes in each of these files (except for Canada). 

		label = True
		boundary_merge('region', 'region_shapefiles_' + str(year), 
                                detected_fires_table, label)
		boundary_merge('county', 'county_shapefiles_' + str(year), 
                                 detected_fires_table, label)
		boundary_merge('state', 'state_shapefiles_' + str(year), 
                                detected_fires_table, label)
