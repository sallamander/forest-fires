import pickle

columns_dict = {'year': 'all_dummies', 'month': 'all_dummies', 'fire_bool': 'bool_col', 'state_name': 'all_dummies'}

with open('makefiles/columns_dict.pkl', 'w+') as f: 
	pickle.dump(columns_dict, f)
