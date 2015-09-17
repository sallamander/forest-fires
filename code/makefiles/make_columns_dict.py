import pickle

columns_dict = {'year': {'transformation': 'all_dummies'}, 
				'month': {'transformation': 'all_dummies'}, 
				'fire_bool': {'transformation': 'bool_col'}, 
				'county_name': {'transformation': 'return_top_n', 'n': 25, 'manip_type': 'eval', 
				'eval_string': 'fire_bool - conf', 'new_col': 'fire_conf_diff'}}

with open('makefiles/columns_dict.pkl', 'w+') as f: 
	pickle.dump(columns_dict, f)
