import pickle

columns_dict = {'year': {'transformation': 'all_dummies'}, 
				'month': {'transformation': 'all_dummies'}, 
				'fire_bool': {'transformation': 'bool_col'}, 
				'urban_area_bool': {'transformation': 'bool_col'}, 
				'land_water_ratio': {'transformation': 'create_new_col', 'eval_string': 'county_aland / county_water', 
				'delete_columns': ['county_aland', 'county_water'], 'replace_nulls': True}, 
				'sat_src': {'transformation': 'all_dummies'}}

with open('makefiles/columns_dict.pkl', 'w+') as f: 
	pickle.dump(columns_dict, f)
