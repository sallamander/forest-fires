import pandas as pd
import pickle
import psycopg2

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

def cleanup_duplicates(): 
	'''
	Input: None
	Output: PSQL Data Table

	Within the daily_fire_shapefiles, I have duplicate entries for a given fire_name and 
	date, which is causing issues when I am merging the daily_fire_shapefiles table onto the 
	detected_fires table. Namely, since I'm meriging on date and geometry, some detected_fires
	centroids in the detected_fires table get merged into multiple fire perimeters, which 
	shouldn't happen (especially because those multiple fire perimeters are actually the same). 
	''' 
	pass 

if __name__ == '__main__': 
	merge_df()
