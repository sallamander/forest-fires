import os
import urllib

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

	If the zipped_files directory is already created within our data directory, 
	then don't create it. Otherwise create it. 
	''' 

	current_dir_dirs = os.listdir('.')

	if 'zipped_files' not in current_dir_dirs: 
		os.mkdir('zipped_files')

def chk_in_zipped_dirs(): 
	'''
	Input: None
	Output: Possibly a created directory. 

	If the boundary_files and detected_fires folders aren't created within the unzipped directory, 
	then create them. Otherwise, don't. 
	'''

	in_zipped_dirs = os.listdir('./zipped_files') 

	if 'boundary_files' not in in_zipped_dirs: 
		os.mkdir('./zipped_files/boundary_files')
	if 'detected_fires' not in in_zipped_dirs: 
		os.mkdir('./zipped_files/detected_fires')

def chk_in_boundary_dirs(): 
	'''
	Input: None
	Output: Possibly Created Directories. 

	If the county, fire_perimeters, region, and urban_areas folders aren't created within 
	the zipped/boundary_files, then create them. Otherwise, don't. 
	'''

	in_zipped_boundary_dirs = os.listdir('./zipped_files/boundary_files')

	folders_list = ['county', 'fire_perimeters', 'region', 'urban_areas', 'state']

	for folder in folders_list: 
		if folder not in in_zipped_boundary_dirs: 
			os.mkdir('./zipped_files/boundary_files/' + folder)
		folders_list2 = os.listdir('./zipped_files/boundary_files/' + folder + '/')

def chk_in_detected_dirs(): 
	'''
	Input: None
	Output: Possibly Created Directories. 

	If the MODIS folder is not created within the unzipped/detected_fires folder, create it. 
	'''

	in_zipped_detected_dirs = os.listdir('./zipped_files/detected_fires')

	if 'MODIS' not in in_zipped_detected_dirs: 
		os.mkdir('./zipped_files/detected_fires/MODIS')

	in_MODIS_dirs = os.listdir('./zipped_files/detected_fires/MODIS')

def get_MODIS_data(year): 
	'''
	Input: None
	Output: Three zipped files with detected fire perimter boundaries

	Download the MODIS detected fires data and move it to the zipped_files/detected_fires/MODIS/ folder
	'''


	if year==2012: 
		modis_url = 'http://activefiremaps.fs.fed.us/data/fireptdata/modis_fire_2012_366_conus_shapefile.zip'
	if year==2013: 
		modis_url = 'http://activefiremaps.fs.fed.us/data/fireptdata/modis_fire_2013_365_conus_shapefile.zip'
	if year==2014: 
		modis_url = 'http://activefiremaps.fs.fed.us/data/fireptdata/modis_fire_2014_365_conus_shapefile.zip'
	if year==2015: 
		modis_url = 'http://activefiremaps.fs.fed.us/data/fireptdata/modis_fire_2015_264_conus_shapefile.zip'

	filename = str(year) + '.zip'
	urllib.urlretrieve(modis_url, filename)
	os.system('mv {filename} zipped_files/detected_fires/MODIS/'.format(filename=filename))

def get_state_boundary_files(year): 
	'''
	Input: 
	Output: Zipped boundary files

	Download the state perimeter boundary files. 
	'''

	if year <= 2013: 
		state_boundary_url = 'http://www2.census.gov/geo/tiger/GENZ2013/cb_2013_us_state_500k.zip'
	elif year >= 2014: 
		state_boundary_url = 'http://www2.census.gov/geo/tiger/GENZ2014/shp/cb_2014_us_state_500k.zip'

	filename = str(year) + '.zip'
	urllib.urlretrieve(state_boundary_url, filename)
	os.system('mv {filename} zipped_files/boundary_files/state'.format(filename=filename))

def get_county_boundary_files(year): 
	'''
	Input: 
	Output: Zipped boundary files

	Download the county perimter boundary files.  
	'''

	if year <= 2013: 
		county_boundary_url = 'http://www2.census.gov/geo/tiger/GENZ2013/cb_2013_us_county_500k.zip'
	elif year >= 2014: 
		county_boundary_url = 'http://www2.census.gov/geo/tiger/GENZ2014/shp/cb_2014_us_county_500k.zip'

	filename = str(year) + '.zip'
	urllib.urlretrieve(county_boundary_url, filename)
	os.system('mv {filename} zipped_files/boundary_files/county'.format(filename=filename))

def get_region_boundary_files(year): 
	'''
	Input: 
	Output: Zipped boundary files

	Download the region perimeter boundary files. 
	'''

	if year <= 2013: 
		region_boundary_url = 'http://www2.census.gov/geo/tiger/GENZ2013/cb_2013_us_region_500k.zip'
	elif year >= 2014: 
		region_boundary_url = 'http://www2.census.gov/geo/tiger/GENZ2014/shp/cb_2014_us_region_500k.zip'

	filename = str(year) + '.zip'
	urllib.urlretrieve(region_boundary_url, filename)
	os.system('mv {filename} zipped_files/boundary_files/region'.format(filename=filename))

def get_urban_boundary_files(year): 
	'''
	Input: 
	Output: Zipped boundary files

	Download the region perimeter boundary files. 
	'''

	if year <= 2013: 
		urban_boundary_url = 'http://www2.census.gov/geo/tiger/GENZ2013/cb_2013_us_ua10_500k.zip'
	elif year >= 2014: 
		urban_boundary_url = 'http://www2.census.gov/geo/tiger/GENZ2014/shp/cb_2014_us_ua10_500k.zip'

	filename = str(year) + '.zip'
	urllib.urlretrieve(urban_boundary_url, filename)
	os.system('mv {filename} zipped_files/boundary_files/urban_areas/'.format(filename=filename))

def get_detected_fire_boundaries(year): 
	'''
	Input: 
	Output: Zipped boundary files

	Download the region perimeter boundary files. 
	'''

	if year == 2012: 
		fires_boundary_url = 'http://rmgsc.cr.usgs.gov/outgoing/GeoMAC/historic_fire_data/2012_perimeters_dd83.zip'
	elif year == 2013: 
		fires_boundary_url = 'http://rmgsc.cr.usgs.gov/outgoing/GeoMAC/historic_fire_data/2013_perimeters_dd83.zip'
	elif year == 2014: 
		fires_boundary_url = 'http://rmgsc.cr.usgs.gov/outgoing/GeoMAC/historic_fire_data/2014_perimeters_dd83.zip'
	elif year == 2015: 
		fires_boundary_url = 'http://rmgsc.cr.usgs.gov/outgoing/GeoMAC/current_year_fire_data/current_year_all_states/perimeters_dd83.zip'

	filename = str(year) + '.zip'
	urllib.urlretrieve(fires_boundary_url, filename)
	os.system('mv {filename} zipped_files/boundary_files/fire_perimeters/'.format(filename=filename))

if __name__ == '__main__': 
	check_dirs()
	for year in [2012, 2013, 2014, 2015]: 
		get_MODIS_data(year)
		get_detected_fire_boundaries(year)

	for year in [2013, 2014]: 
		get_state_boundary_files(year)
		get_county_boundary_files(year)
		get_region_boundary_files(year)
		get_urban_boundary_files(year)

