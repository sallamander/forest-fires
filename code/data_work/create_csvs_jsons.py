import psycopg2
import os

def output_csv(year): 
	'''
	Input: Intger
	Output: CSV file

	Ouptut the postgres detected_fires table for the inputted year into a .csv. 
	'''

	check_dir('csvs')

	conn = pscycopg2.connect('dbname=forest_fires', user=os.environ['USER'], host='localhost')
	cursor = conn.cursor()

	conn.execute('''COPY detected_fires_{year} to 
				'../data/csvs/detected_fires_{year}.csv' DELIMITER AS ',' 
				CSV HEADER;'''.format(str(year)))

def check_dir(data_dir_name): 
	'''
	Input: None
	Output: Possibly Created Directory/Folder

	Check to make sure the data/data_dir_name directory/folder is created, and if not create it. 
	'''

	# In the hopes of generalizing this so I can easily throw it up on AWS or somebody else can 
	# use it, I'm going to find the current directory path, remove any directories /forest-fires
	# and deeper, and then create the data_dir_name in forest-fires/data/data_dir_name. 
	current_dir = os.getcwd()
	location = current_dir.find('forest-fires')

	if location == -1: 
		raise Exception("You're not running this code from anywhere in you're forest-fire directory... \
						Smokey would be ashamed!")
	else: 
		data_dirs = os.listdir(current_dir[:location] + '/forest-fires/data/')
		if data_dir_name not in data_dirs: 
			os.mkdir(current_dir[:location] + '/forest-fires/data/' + data_dir_name)


if __name__ == '__main__': 
	for year in xrange(2013, 2015): 
		output_csv(year)

