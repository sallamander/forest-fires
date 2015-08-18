import os

def create_dirs(): 
	'''
	Input: None
	Output: Folders 

	Create a folder for each year of data that I will be grabbing, and for 
	each type of satellite (MODIS, VIIRS, or VIIRS_I). 
	'''

	for year in range(2001, 2016): 
		os.makedirs('../../data/raw_data/MODIS/' + str(year))

	for year in range(2012, 2016): 
		os.makedirs('../../data/raw_data/VIIRS/' + str(year))

	for year in range(2014, 2016): 
		os.makedirs('../../data/raw_data/VIIRS_I/' + str(year))
