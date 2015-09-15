import pickle

columns_dict = {'year': {'transformation': 'all_dummies'}, 'month': {'transformation': 'all_dummies'}, 
			'fire_bool': {'transformation': 'bool_col'}, 'state_name': {'transformation': 'return_n', 'n': 5, 
			'dummies_to_grab': 'both'}}

with open('makefiles/columns_dict.pkl', 'w+') as f: 
	pickle.dump(columns_dict, f)
