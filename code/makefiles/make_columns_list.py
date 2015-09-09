import pickle

columns_list = ['date', 'lat', 'long', 'conf', 'fire_bool']

with open('makefiles/columns_list.pkl', 'w+') as f: 
	pickle.dump(columns_list, f)
