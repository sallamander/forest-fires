import pandas as pd
import sys
import pickle

from data_manip.general_featurization import combine_dfs, grab_columns, return_all_dummies
from data_manip.time_featurization import break_time_col



if __name__ == '__main__': 
	with open('../makefiles/year_list.pkl') as f: 
		year_list = pickle.load(f)
	with open('../makefiles/columns_list.pkl') as f: 
		columns_list = pickle.load(f)

	dfs_list = []
	for year in year_list: 
		df_path = '../../data/csvs/fires_' + str(year) + '.csv'
		df = pd.read_csv(df_path)
		dfs_list.append(df)

	df = combine_dfs(dfs_list)
	df = grab_columns(df, columns_list)
	df = break_time_col(df, 'date')

