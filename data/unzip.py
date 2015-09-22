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

	if 'unzipped_files' not in current_dir_dirs: 
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

	folders_list = ['county', 'fire_perimeters', 'region', 'urban_areas', 'state']

	for folder in folders_list: 
		if folder not in in_unzipped_boundary_dirs: 
			os.mkdir('./unzipped_files/boundary_files/' + folder)
		folders_list2 = os.listdir('./unzipped_files/boundary_files/' + folder + '/')
<<<<<<< HEAD
		for year in xrange(2013, 2016): 
=======
		for year in xrange(2012, 2016): 
>>>>>>> ee23f2fa9b27de4f9b5ad0d0b7213d8ae43d6e28
			folder2 = './unzipped_files/boundary_files/' + folder + '/' + str(year)
			if str(year) not in folders_list2: 
				os.mkdir(folder2)


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

<<<<<<< HEAD
	for year in xrange(2013, 2016): 
=======
	for year in xrange(2012, 2016): 
>>>>>>> ee23f2fa9b27de4f9b5ad0d0b7213d8ae43d6e28
		if str(year) not in in_MODIS_dirs: 
			os.mkdir('./unzipped_files/detected_fires/MODIS/' + str(year))

def unzip_files(): 
	'''
	Input: None
	Output: Unzipped Files. 

	For all of the created dirs. above, let's unzip the data from the zipped files. I'm going 
	to assume that the user wants to unzip this only once, and so I'm going to remove all files 
	from the unzipped dirs. created above (purge them), and I'm going to remove everything but 
	the remaining zipped files from all of the zipped folders. 
	'''

	unzip_boundaries()
	unzip_detected()

def unzip_boundaries():
	'''
	Input: None
	Output: Unzipped files. 

	Unzip all of the files in each of the boundary folders and move them from the zipped folder
	to the equivalent unzipped folder. 
	''' 

	boundaries_dirs = os.listdir('./zipped_files/boundary_files')
	current_dir = os.getcwd()

	for bound_dir in boundaries_dirs: 
		os.chdir(current_dir)
		if bound_dir != '.DS_Store': 
			filepath = './zipped_files/boundary_files/' + bound_dir + '/'
			os.chdir(current_dir + filepath[1:])
			remove_nonzips()
			zipped_files = os.listdir('./')
			for zipped_file in zipped_files: 
<<<<<<< HEAD
				if zipped_file == '2015.zip' and bound_dir == 'fire_perimeters': 
					unzip_2015_fire_perimeters()
				else: 
					os.system('unzip ' + zipped_file)
=======
				os.system('unzip ' + zipped_file)
>>>>>>> ee23f2fa9b27de4f9b5ad0d0b7213d8ae43d6e28
			mv_nonzips()


	os.chdir(current_dir)

def remove_nonzips(): 
	'''
	Input: None
	Output: None

	Within the current working directory, delete/remove all files which aren't .zip files. 
	'''

	files = os.listdir('./')

	for f in files:
		if f.find('.zip') == -1: 
			os.remove(f)

def mv_nonzips(): 
	'''
	Input: None
	Output: None
	
	Within the current working directory, move all those files without .zip extensions (i.e. 
	the recently unzipped files) to the equivalent folder in the unzipped folder in the data	
	folder. 
	'''

	files = os.listdir('./')
	current_dir = os.getcwd()
	move_to_dir = current_dir.replace('zipped_files', 'unzipped_files')

	for f in files: 
<<<<<<< HEAD
		if f.find('2013') != -1 and f.find('.zip') == -1: 
			os.rename(current_dir + '/' + f, move_to_dir + '/2013/' + f)
		if f.find('2014') != -1 and f.find('.zip') == -1: 
			os.rename(current_dir + '/' + f, move_to_dir + '/2014/' + f)
		if f.find('2015') != -1: 
			if current_dir.find('fire_perimeters') != -1: 
				mv_2015_fire_perimeters(current_dir, move_to_dir)
			elif f.find('.zip') == -1: 
				os.rename(current_dir + '/' + f, move_to_dir + '/2015/' + f)
=======
		if f.find('2012') != -1 and f.find('.zip') == -1: 
			os.rename(current_dir + '/' + f, move_to_dir + '/2012/' + f)
		elif f.find('2013') != -1 and f.find('.zip') == -1: 
			os.rename(current_dir + '/' + f, move_to_dir + '/2013/' + f)
		elif f.find('2014') != -1 and f.find('.zip') == -1: 
			os.rename(current_dir + '/' + f, move_to_dir + '/2014/' + f)
		elif f.find('.zip') == -1: 
			os.rename(current_dir + '/' + f, move_to_dir + '/2015/' + f)
>>>>>>> ee23f2fa9b27de4f9b5ad0d0b7213d8ae43d6e28

def unzip_detected(): 
	'''
	Input: None
	Output: None

	Unzip all of the files in each of the detected fires folders and move them from the zipped folder
	to the equivalent unzipped folder. 
	'''

	detected_fires_dirs = os.listdir('./zipped_files/detected_fires')
	current_dir = os.getcwd()

	for detected_fire_dir in detected_fires_dirs: 
		os.chdir(current_dir)
		if detected_fire_dir != '.DS_Store': 
			filepath = './zipped_files/detected_fires/' + detected_fire_dir + '/'
			os.chdir(current_dir + filepath[1:])
			remove_nonzips()
			zipped_files = os.listdir('./')
			for zipped_file in zipped_files: 
				os.system('unzip ' + zipped_file)
			mv_nonzips()

<<<<<<< HEAD
def unzip_2015_fire_perimeters(): 
	'''
	Input: None
	Output: Unzipped and moved files

	The 2015 fire perimters files were too big to .zip up in a way that didn't exceed github's 100 MB restriction, 
	so I found a way around that by using tar to split up the .shp file into two pieces and .tar those pieces (this 
	was the one file in the 2015 fire perimeters data that was causing the problem - even zipped it's 135 MB). 
	This function is built to unzip those pieces, since it takes a special unzip command than is typical for the
	other .zip files that I have stored the perimeter boundaries in. It's also worth nothing (and I'll note this
	in the README that the 2015.zip folder for the fire_perimeters isn't actually a .zip; it simplified the code 
	to rename it to a .zip), and everything that could be zipped is already stored within that 2015.zip folder (i.e. 
	the .shp file I just mentioned tarring).  

	For the record, this is the command I used to break up the .shp file was: 

	tar -cf - 2015_perimeters_dd83.shp | split -b 90m - 2015_perimeters_dd83.shp.tar
	''' 

	os.chdir('./2015.zip')
	os.system('cat 2015_perimeters_dd83.shp.tara* | (tar x)')
	os.chdir('../')

def mv_2015_fire_perimeters(current_dir, move_to_dir): 
	'''
	Input: String, String
	Output: Moved files

	This is the analgous move function to the unzip_2015_fire_perimeters function. 
	'''

	os.chdir('./2015.zip')
	files = os.listdir('./')
	for f in files: 
		if f.find('.tar') == -1:
			os.system('cp {current_dir}/2015.zip/{f} {move_to_dir}/2015/{f}'.format(current_dir=current_dir,
					  move_to_dir=move_to_dir, f=f))

	os.system('rm -r 2015_perimeters_dd83.shp')
	os.chdir('./')

=======
>>>>>>> ee23f2fa9b27de4f9b5ad0d0b7213d8ae43d6e28
if __name__ == '__main__': 
	check_dirs()
	unzip_files()