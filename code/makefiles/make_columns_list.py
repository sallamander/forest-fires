import pickle

columns_list = ['lat', 'long', 'frp', 'date_fire', 'fire_bool', 'urban_area_bool', 
				'county_aland', 'county_water', 'gmt', 'temp', 'conf']

'''
dewPoint, humidity
'''

with open('makefiles/columns_list.pkl', 'w+') as f: 
	pickle.dump(columns_list, f)
