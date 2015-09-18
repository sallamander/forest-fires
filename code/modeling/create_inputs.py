import pandas as pd
import sys
import pickle

from data_manip.general_featurization import combine_dfs, grab_columns, \
		return_all_dummies, boolean_col, return_top_n, create_new_col, return_outlier_boolean
from data_manip.time_featurization import break_time_col




if __name__ == '__main__': 
	with open('./makefiles/year_list.pkl') as f: 
		year_list = pickle.load(f)
	with open('./makefiles/columns_list.pkl') as f: 
		columns_list = pickle.load(f)
	with open('./makefiles/columns_dict.pkl') as f: 
		columns_dict = pickle.load(f)

	dfs_list = []
	for year in year_list: 
		df_path = '../data/csvs/fires_' + str(year) + '.csv'
		df = pd.read_csv(df_path)
		dfs_list.append(df)

	df = combine_dfs(dfs_list)
	df = grab_columns(df, columns_list)
	df = break_time_col(df, 'date_fire')

	featurization_dict = {'all_dummies': return_all_dummies, 'bool_col': boolean_col, 'return_top_n': return_top_n, 
						'create_new_col': create_new_col, 'outlier_boolean': return_outlier_boolean}

	for k, v in columns_dict.iteritems(): 
		df = featurization_dict[v['transformation']](df, k, v)

	with open('./modeling/input_df.pkl', 'w+') as f: 
		pickle.dump(df, f)
