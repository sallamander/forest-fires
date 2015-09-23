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

def calc_bins(df, col, num_bins): 
	'''
	Input: Pandas DataFrame, Integer
	Output: 2D Numpy Array
	'''

	bin_breaks = np.linspace(0, 1, num_bins + 1)

	model_dict = {}
	for idx in xrange(num_bins):
		bin_bottom, bin_top = bin_breaks[idx], bin_breaks[idx + 1]
		fires_query = 'fire_bool == 1 and ' + col + ' > ' + str(bin_bottom) + ' and ' + col + ' < ' + str(bin_top)
		non_fires_query = 'fire_bool == 0 and ' + col + ' > ' + str(bin_bottom) + ' and ' + col + ' < ' + str(bin_top)
		fires = df.query(fires_query).count()[col] 
		non_fires = df.query(non_fires_query).count()[col] 

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


def output_d3_csv(final_groups): 
	'''
	Input: List of dictionaries
	Ouput: Saved CSV
	'''

	output_df = pd.DataFrame(final_groups)

	import pdb
	pdb.set_trace()
	output_df.to_csv('model_preds.csv')

if __name__ == '__main__': 
	df = pd.read_csv('../../data/csvs/model_preds.csv')

	num_bins = 5
	final_groups = output_preds_hist(df, num_bins)

	'''
	model_name = 'gradient_boosting'
	plot_model(final_groups, model_name, num_bins)
	'''
	output_d3_csv(final_groups)

