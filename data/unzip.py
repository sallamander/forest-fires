import os

def check_dirs(): 
	'''
	Input: 
	Output: Potentially created dirs

	Navigate the folder structure and make sure that the correct folders
	are created for us to unzip the zipped data into.  
	'''


	chk_zipped_dir() 
	chk_in_zipped_dirs()	
	chk_in_boundary_dirs()
	chk_in_detected_dirs()

def chk_zipped_dir(): 
	'''
	Input: None
	Output: Possibly a created directory

	If the unzipped_files directory is already created within our data directory, 
	then don't create it. Otherwise create it. 
	''' 

	current_dir_dirs = os.listdir('.')

	if 'unzipped_files' not in current_dir_dirs; 
		os.mkdir('unzipped_files')

def chk_in_zipped_dirs(): 
	'''
	Input: None
	Output: Possibly a created directory. 

	If the boundary_files and detected_fires folders aren't created within the unzipped directory, 
	then create them. Otherwise, don't. 
	'''

	in_unzipped_dirs = os.listdir('./unzipped_files') 

	if 'boundary_files' not in in_unzipped_dirs: 
		os.mkdir('./unzipped_files/boundary_files')
	if 'detected_fires' not in in_unzipped_dirs: 
		os.mkdir('./unzipped_files/detected_fires')

def chk_in_boundary_dirs(): 
	'''
	Input: None
	Output: Possibly Created Directories. 

	If the county, fire_perimeters, region, and urban_areas folders aren't created within 
	the unzipped/boundary_files, then create them. Otherwise, don't. 
	'''

	in_unzipped_boundary_dirs = os.listdir('./unzipped_files/boundary_files')

	folders_list = ['county', 'fire_perimeters', 'region', 'urban_areas']

	for folder in folders_list: 
		if folder not in in_unzipped_boundary_dirs: 
			os.mkdir('./unzipped_files/boundary_files/' + folder)

def chk_in_detected_dirs(): 
	'''
	Input: None
	Output: Possibly Created Directories. 

	If the MODIS folder is not created within the unzipped/detected_fires folder, create it. Within 
	that MODIS folder, if 2013, 2014, and 2015 folders are not creted, create those. 
	'''

	in_unzipped_detected_dirs = os.listdir('./unzipped_files/detected_fires')

	if 'MODIS' not in in_unzipped_detected_dirs: 
		os.mkdir('./unzipped_files/detected_fires/MODIS')

	in_MODIS_dirs = os.listdir('./unzipped_files/detected_fires/MODIS')

	for year in xrange(2013, 2016): 
		if str(year) not in in_MODIS_dirs: 
			os.mkdir('./unzipped_files/detected_fires/MODIS/' + str(year))


if __name__ == '__main__': 
	check_dirs()