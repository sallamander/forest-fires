import pickle

columns_list = ['lat', 'long', 'frp', 'date_fire', 'conf', 'fire_bool', 'urban_area_bool', 
				'county_aland', 'county_water', 'gmt', 'temp']

with open('makefiles/columns_list.pkl', 'w+') as f: 
	pickle.dump(columns_list, f)
