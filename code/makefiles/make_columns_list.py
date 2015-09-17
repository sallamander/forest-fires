import pickle

columns_list = ['lat', 'long', 'frp', 'date_fire', 'conf', 'fire_bool', 'urban_area_bool']

with open('makefiles/columns_list.pkl', 'w+') as f: 
	pickle.dump(columns_list, f)
