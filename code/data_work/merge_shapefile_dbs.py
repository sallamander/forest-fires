import pandas as pd
import pickle
import psycopg2


'''
For trues/falses (whether fire or not and whether urban area), input 
variable name and table to query from. 
'''

def boundary_bool_merge(new_col_name, shapefile_table_name, detected_fires_table):
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
	conn = psycopg2.connect('dbname=forest_fires')
	cursor = conn.cursor()

	cursor.execute('''ALTER TABLE {detected_fires_table}
						DROP COLUMN IF EXISTS {new_col_name};
					'''.format(detected_fires_table=detected_fires_table, 
								new_col_name=new_col_name))

	query = create_bool_query(new_col_name, shapefile_table_name, detected_fires_table)
	cursor.execute(query)

	cursor.execute(''' DROP TABLE {}'''.format(detected_fires_table))
	cursor.execute(''' ALTER TABLE {detected_fires_table}2 
						RENAME TO {detected_fires_table}'''.format(detected_fires_table=detected_fires_table))

	conn.commit()
	conn.close()

def create_bool_query(new_col_name, shapefile_table_name, detected_fires_table): 
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

	# If we are adding in a fire column, then we will be merging using the fire perimeter 
	# boundaries, which means we're merging on date and geometry. 
	on_query_part = 'ST_WITHIN(points.wkb_geometry, polys.wkb_geometry)'

	if new_col_name == 'fire': 
		on_query_part += ' AND points.date = polys.date_'


	# The breakdown of this query ... kind of from the inside out.
	#  
	# 1.) Merge the detected fires data with whatever shapefile is inputted, and keep track 
	# 	of only the unique lat, long, date in a temporary table (called merged). 
	# 2.) Merge the detected fires data table with merged and along the way create a 
	#  	boolean that holds whether each row of the detected fire data table was within 
	# 	shape perimeter boundary. 
	# 3.) Create a new table holding these results. 
	query = '''CREATE TABLE {detected_fires_table}2 AS 
						(WITH merged AS
							(SELECT DISTINCT lat, long, date FROM 
						 		(SELECT lat, long, date
									FROM {detected_fires_table} as points
									INNER JOIN {shapefile_table_name} as polys
						 				ON {on_query_part}) as merged
							)  

						SELECT df.*, 
							CASE WHEN merged.lat IS NOT NULL THEN TRUE
								 WHEN merged.lat IS NULL THEN FALSE END AS {new_col_name}
						FROM {detected_fires_table} df
						LEFT JOIN merged 
							ON df.lat = merged.lat
							AND df.long = merged.long
							AND df.date = merged.date
						);
						'''.format(detected_fires_table=detected_fires_table, 
									shapefile_table_name=shapefile_table_name, 
									new_col_name=new_col_name, on_query_part=on_query_part)
	return query

if __name__ == '__main__': 
	for year in xrange(2013, 2015): 
		detected_fires_table = 'detected_fires_' + str(year)
		boundary_bool_merge('fire', 'perimeters_shapefiles_' + str(year), detected_fires_table)
		boundary_bool_merge('urban_area', 'urban_shapefiles_' + str(year), detected_fires_table)
