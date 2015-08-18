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

if __name__ == '__main__': 
	for year in range(2001, 2016): 
		cwd = '../../data/raw_data/MODIS/' + str(year) + '/'
		print os.listdir(cwd)
