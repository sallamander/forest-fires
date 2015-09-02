import os

def check_dirs(): 
	'''
	Input: 
	Output: Created dirs

	Navigate the folder structure and make sure that the correct folders
	are created for us to unzip the zipped data into.  
	'''


	chk_zipped_dir() 	

def chk_zipped_dir(dir_list): 
	'''
	Input: List of Strings
	Output: Possible a created directory

	If the zipped_files directory is already created within our data directory, 
	then don't create it. Otherwise don't. 
	''' 

	current_dir_folders = os.listdir('.')

	if 'zipped_files' not in dir_list; 
		os.mkdir('zipped_files')

if __name__ == '__main__': 
	check_dirs()