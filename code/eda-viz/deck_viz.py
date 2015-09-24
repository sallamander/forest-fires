import pandas as pd
import numpy as np
import json
from collections import defaultdict

def output_preds_hist(df, num_bins=5): 
	'''
	Input: Pandas DataFrame, Integer
	Output: Seaborn histogram 

	For the inputted df, lets bin the probability of fire into the number of inputted bins, and then 
	let's see how our fire prediction is in each bin. 
	'''
	final_groupings = []
	for col in df.columns:
		if col != 'fire_bool': 	
			model_groupings = calc_bins(df, col, num_bins)
			final_groupings.append(model_groupings)

	return final_groupings

def calc_bins(df, col, num_bins, str_name = None): 
	'''
	Input: Pandas DataFrame, Integer
	Output: dictionary
	'''

	bin_breaks = np.linspace(0, 1, num_bins + 1)

	model_dict = {}
	for idx in xrange(num_bins):
		bin_bottom, bin_top = bin_breaks[idx], bin_breaks[idx + 1]
		fires_query = 'fire_bool == 1 and ' + col + ' > ' + str(bin_bottom) + ' and ' + col + ' < ' + str(bin_top)
		non_fires_query = 'fire_bool == 0 and ' + col + ' > ' + str(bin_bottom) + ' and ' + col + ' < ' + str(bin_top)
		fires = df.query(fires_query).count()[col] 
		non_fires = df.query(non_fires_query).count()[col] 

		if str_name is not None: 
			model_dict['model_name'] = str_name
		else: 
			model_dict['model_name'] = col
		model_dict[str(bin_bottom) + '-' + str(bin_top)] = float(fires) / (fires + non_fires + 1)

	return model_dict

def plot_model(final_groups, model_name, num_bins): 
	'''
	Input: Dictionary of dictionaries, String, Integer
	Output: Seaborn Stacked Plot
	'''

	df = pd.DataFrame()
	df['group'] = np.linspace(0, 1, num_bins + 1)[:-1]
	df['percentage'] = np.array(final_groups[model_name][1]).astype(float) / (np.array(final_groups[model_name][0]) + np.array(final_groups[model_name][1]))

	sns.barplot(x = df.group, y = df.percentage)

	# topbar = plt.Rectangle((0,0),1,1,fc="red", edgecolor = 'none')
	# bottombar = plt.Rectangle((0,0),1,1,fc='#0000A3',  edgecolor = 'none')


def output_d3_csv(final_groups, csv_name): 
	'''
	Input: List of dictionaries
	Ouput: Saved CSV
	'''

	output_df = pd.DataFrame(final_groups)
	output_df.to_csv(csv_name)

def output_fine_preds(df, num_bins): 
	'''
	Input: Pandas DataFrame, integer
	Output: Pandas DataFrame
	'''
	final_groupings = []
	for col in df.columns:
		if col != 'fire_bool': 	
			model_groupings = calc_bins2(df, col, num_bins)
			final_groupings.append(model_groupings)

	return final_groupings

def calc_bins2(df, col, num_bins): 
	'''
	Input: Pandas DataFrame, string, Integer
	Output: Dictionary
	'''

	model_dict = defaultdict(list)
	bin_breaks = np.linspace(0, 1, num_bins + 1)
	for idx in xrange(num_bins):
		bin_bottom, bin_top = bin_breaks[idx], bin_breaks[idx + 1]
		fires_query = 'fire_bool == 1 and ' + col + ' > ' + str(bin_bottom) + ' and ' + col + ' < ' + str(bin_top)
		non_fires_query = 'fire_bool == 0 and ' + col + ' > ' + str(bin_bottom) + ' and ' + col + ' < ' + str(bin_top)

		fires = df.query(fires_query).count()[col] 
		non_fires = df.query(non_fires_query).count()[col] 
		percent_fires = float(fires) / (fires + non_fires + 1)

		model_dict[col].append(percent_fires)

	return model_dict

def output_gboosting_preds_hist(num_bins): 
	'''
	Input: List of dictionaries
	Output: List of dictionaries
	'''

	filenames = ['../../data/csvs/model_preds_conf_60.csv', '../../data/csvs/model_preds_lessconf_60.csv', '../../data/csvs/model_preds2_60.csv']

	gboosting_list = []
	for idx, filename in enumerate(filenames):
		df = pd.read_csv(filename)
		feature_set_name = get_feature_set_name(idx)
		feature_dict = calc_bins(df, 'gradient_boosting', num_bins, feature_set_name)
		gboosting_list.append(feature_dict)

	return gboosting_list


def get_feature_set_name(idx): 
	'''
	Input: Integer
	Output: String
	'''

	if idx == 0: 
		return 'confidence only'
	elif idx == 1: 
		return 'geo only'
	elif idx == 2: 
		return 'confidence + geo'

if __name__ == '__main__': 
	df = pd.read_csv('../../data/csvs/model_preds2_60.csv')

	num_bins = 5
	final_groups = output_preds_hist(df, num_bins)

	g_boosting_groups = output_gboosting_preds_hist(num_bins)

	'''
	num_bins = 50
	fine_final_groups = output_fine_preds(df, num_bins)
	model_name = 'gradient_boosting'
	plot_model(final_groups, model_name, num_bins)
	'''
	output_d3_csv(final_groups, 'model_preds.csv')
	output_d3_csv(g_boosting_groups, 'gboosting_preds.csv')

