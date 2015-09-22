import pickle

<<<<<<< HEAD:code/makefiles/make_year_list.py
year_list = [2013, 2014, 2015]
=======
year_list = [2012]
>>>>>>> ee23f2fa9b27de4f9b5ad0d0b7213d8ae43d6e28:code/makefiles/make_year_list.py

with open('makefiles/year_list.pkl', 'w+') as f: 
	pickle.dump(year_list, f)
