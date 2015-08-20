import shapefile
import pandas as pd
import os
import numpy as np
import reverse_geocoder as rg
from pickle import dump 
from collections import defaultdict

def read_file(year, basefile_name): 
	'''
	Input: String
	Output: Pandas DataFrame

	Read in the shapefiles from the given filepath and translate the result into a 
	pandas dataframe. 
	'''
	filepath = '../../data/raw_data/MODIS/' + str(year) + '/' + basefile_name
	
	sf = shapefile.Reader(filepath)
	# The first field is simply a spec that we don't actually want. 
	col_names = [field[0] for field in sf.fields[1:]]
	df = pd.DataFrame(sf.records(), columns=col_names)

	if year<=2008: 
		df = format_df(df)
	else: 
		df = df.drop('SRC', axis=1)

	df['year'] = year
	df = get_state2(df)

	return df, sf

def get_basefile_name(year): 
	'''
	Input: Integer
	Output: String

	Take in the given year, navigate to the satellite data for that year, and 
	pull the basefile name that the shapefile library will need to put all 
	of the files together. 
	'''
	current_dir = '../../data/raw_data/MODIS/' + str(year) + '/'
	files = os.listdir(current_dir)

	ext_index = files[0].find('.')
	basefile_name = files[0][:ext_index]
	return basefile_name

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

def pickle_df_sf(df, sf): 


def get_reverse_geocode(df): 
	'''
	Input: Pandas DataFrame
	Output: Pandas DataFrame

	Take the latitude/longitude coordinates for each row in the DataFrame, and get the country, state, 
	and county information and put those in the DataFrame. 
	'''

	geo_info = defaultdict(list)
	df = df.loc[0:50].copy()
	for idx, lat in enumerate(df['LAT']): 
		coords = (lat, df.loc[idx, 'LONG'])
		print idx, coords
		results = rg.search(coords)[0]


		geo_info['country'].append(results['cc'])
		geo_info['state'].append(results['admin1'])
		geo_info['county'].append(results['admin2'])


	df['country'] = geo_info['country']
	df['state'] = geo_info['state']
	df['county'] = geo_info['county']

	return df


if __name__ == '__main__': 
	for year in range(2001, 2002): 
		basefile_name = get_basefile_name(year)
		shapefile_df, shapefile_sf = read_file(year, basefile_name)
		pickle_df_sf(shapefile_df, shapefile_sf)

		
