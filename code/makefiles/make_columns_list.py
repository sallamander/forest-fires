import pickle

columns_list = ['date_fire', 'conf', 'fire_bool', 'state_name']

with open('makefiles/columns_list.pkl', 'w+') as f: 
	pickle.dump(columns_list, f)
