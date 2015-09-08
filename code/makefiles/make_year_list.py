import pickle

year_list = [2013, 2014, 2015]

with open('makefiles/year_list.pkl', 'w+') as f: 
	pickle.dump(year_list, f)
