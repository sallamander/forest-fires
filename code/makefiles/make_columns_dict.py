import pickle

columns_dict = {'year': {'transformation': 'all_dummies'}, 
				'month': {'transformation': 'all_dummies'}, 
				'fire_bool': {'transformation': 'bool_col'}, 
				'urban_area_bool': {'transformation': 'bool_col'}}

with open('makefiles/columns_dict.pkl', 'w+') as f: 
	pickle.dump(columns_dict, f)
