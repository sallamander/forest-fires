import shapefile
import pandas as pd
import os

def read_file(filepath): 
	'''
	Input: String
	Output: Pandas DataFrame

	Read in the shapefiles from the given filepath and translate the result into a 
	pandas dataframe. 
	'''

	sf = shapefile(filepath)
	# The first field is simply a spec that we don't actually want. 
	col_names = [field[0] for field in sf.fields[1:]]
	df = pd.dataFrame(sf, columns=col_names)

	return df

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

if __name__ == '__main__': 
	for year in range(2001, 2016): 
		print get_basefile_name(year)
		
