"""A tiny script to pickle the list of years to be used in modeling."""
import pickle

year_list = [2012, 2013, 2014, 2015]

with open('code/makefiles/year_list.pkl', 'w+') as f: 
	pickle.dump(year_list, f)
