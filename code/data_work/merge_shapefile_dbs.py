import pandas as pd
import pickle
import psycopg2


'''
For trues/falses (whether fire or not and whether urban area), input 
variable name and table to query from. 
'''

def merge_df():
	'''
	Input: None
	Output: PSQL Data Table
	'''
	conn = psycopg2.connect('dbname=forest_fires')
	cursor = conn.cursor()

	cursor.execute(''' CREATE TABLE merged_boundary AS
						
					(SELECT DISTINCT lat FROM 
					 (SELECT points.*, polys.fire_name
					 FROM detected_fires_2013 as points
							INNER JOIN perimeters_shapefiles_2013 as polys
					 ON points.date = polys.date_ 
					 	AND ST_WITHIN(points.wkb_geometry, polys.wkb_geometry)) as temp_fires);  

					CREATE TABLE ff2 as 
						SELECT df.*, 
							CASE WHEN ff.lat IS NOT NULL THEN TRUE
								 WHEN ff.lat IS NULL THEN FALSE END AS fire
						FROM detected_fires_2013 df
						LEFT JOIN ff 
							ON df.lat = ff.lat; 
					''')

	conn.commit()
	conn.close()

if __name__ == '__main__': 
	merge_df()
