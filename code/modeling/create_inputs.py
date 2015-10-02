import pandas as pd
import sys
import pickle

from data_manip.general_featurization import combine_dfs, grab_columns, \
		return_all_dummies, boolean_col, return_top_n, create_new_col, return_outlier_boolean
from data_manip.time_featurization import break_time_col
from data_manip.geo_featurization import gen_nearby_fires_count

if __name__ == '__main__': 
	with open('./makefiles/year_list.pkl') as f: 
		year_list = [2012, 2013, 2014, 2015]
	with open('./makefiles/columns_list.pkl') as f: 
		columns_list = pickle.load(f)
	with open('./makefiles/columns_dict.pkl') as f: 
		columns_dict = pickle.load(f)

	dfs_list = []
	for year in year_list: 
		df_path = '../data/csvs/fires_weather_' + str(year) + '.csv'
		df = pd.read_csv(df_path)
		dfs_list.append(df)


	df = combine_dfs(dfs_list)
	df = break_time_col(df, 'date_fire')

	nearby_fires_df_filepath = './modeling/nearby_done_df_' + str(columns_dict['add_nearby_fires']['dist_measure']) + '.pkl'
	# This process takes awhile, and I won't need to do it each time. 
	if 'nearby_fires_done' not in columns_dict.keys(): 
		dist_measure = columns_dict['add_nearby_fires']['dist_measure']
		time_measures = columns_dict['add_nearby_fires']['time_measures']
		df = gen_nearby_fires_count(df, dist_measure, time_measures, columns_dict['add_nearby_fires']['rate_measures'])
		with open(nearby_fires_df_filepath, 'w') as f: 
			pickle.dump(df, f)
	else: 
		with open(nearby_fires_df_filepath) as f:
			df = pickle.load(f)

	df = grab_columns(df, columns_list)
	featurization_dict = {'all_dummies': return_all_dummies, 'bool_col': boolean_col, 'return_top_n': return_top_n, 
						'create_new_col': create_new_col, 'outlier_boolean': return_outlier_boolean}

	for k, v in columns_dict.iteritems(): 
		if k != 'add_nearby_fires':
			df = featurization_dict[v['transformation']](df, k, v)
	
	input_df_filename = './modeling/input_df_' + str(columns_dict['add_nearby_fires']['dist_measure']) + '.pkl'
	with open(input_df_filename, 'w+') as f: 
		pickle.dump(df, f)
