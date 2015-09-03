import pandas as pd
import pickle
import psycopg2


'''
For trues/falses (whether fire or not and whether urban area), input 
variable name and table to query from. 
'''

def boundary_bool_merge(new_col_name, shapefile_table_name, detected_fires_table):
	'''
	Input: None
	Output: PSQL Data Table
	'''
	conn = psycopg2.connect('dbname=forest_fires')
	cursor = conn.cursor()

	cursor.execute(''' CREATE TABLE ff AS
						
					(SELECT DISTINCT lat, long, date FROM 
					 (SELECT points.*, polys.fire_name
					 FROM ''' + detected_fires_table + '''  as points
							INNER JOIN ''' + shapefile_table_name + ''' as polys
					 ON points.date = polys.date_ 
					 	AND ST_WITHIN(points.wkb_geometry, polys.wkb_geometry)) as temp_fires);  

					CREATE TABLE ff2 as 
						SELECT df.*, 
							CASE WHEN ff.lat IS NOT NULL THEN TRUE
								 WHEN ff.lat IS NULL THEN FALSE END AS ''' + new_col_name + 
					'''
						FROM detected_fires_2013 df
						LEFT JOIN ff 
							ON df.lat = ff.lat
							AND df.long = ff.long
							AND df.date = ff.dat; 
					''')

	conn.commit()
	conn.close()

if __name__ == '__main__': 
	boundary_bool_merge('fire', 'perimeters_shapefiles_2013', 'detected_fires_2013')
