import pickle

columns_dict = {'year': {'transformation': 'all_dummies'}, 
				'month': {'transformation': 'all_dummies'}, 
				'fire_bool': {'transformation': 'bool_col'}, 
				'urban_area_bool': {'transformation': 'bool_col'}, 
				'land_water_ratio': {'transformation': 'create_new_col', 'eval_string': 'county_aland / county_water', 
				'delete_columns': ['county_aland', 'county_water'], 'replace_nulls': True}, 
				'tpix': {'transformation': 'outlier_boolean', 'std_multiplier': 2},
				'state_name': {'transformation': 'return_top_n', 'n': 5, 'manip_type': 'eval', 
							'eval_string': 'fire_bool - conf / 100.0', 'new_col': 'fire_conf_diff'}}

with open('makefiles/columns_dict.pkl', 'w+') as f: 
	pickle.dump(columns_dict, f)
