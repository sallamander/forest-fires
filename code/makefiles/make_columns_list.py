import pickle

columns_list = ['lat', 'long', 'frp', 'date_fire', 'fire_bool', 'urban_area_bool', 
				'county_aland', 'county_water', 'gmt', 'temp', 'conf', 'month', 'year', 
				'nearby_count_1', 'nearby_count_2' ,'nearby_count_3' ,'nearby_count_4'
				,'nearby_count_5' ,'nearby_count_6' ,'nearby_count_7']

'''
dewPoint, humidity
'''

with open('makefiles/columns_list.pkl', 'w+') as f: 
	pickle.dump(columns_list, f)
