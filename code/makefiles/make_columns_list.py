import pickle

columns_list = ['lat', 'long', 'frp', 'date_fire', 'conf', 'fire_bool', 'county_name']

with open('makefiles/columns_list.pkl', 'w+') as f: 
	pickle.dump(columns_list, f)
