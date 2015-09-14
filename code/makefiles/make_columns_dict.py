import pickle

columns_dict = {'year': 'dummy_all', 'month': 'dummy_all'}

with open('makefiles/columns_dict.pkl', 'w+') as f: 
	pickle.dump(columns_dict, f)
