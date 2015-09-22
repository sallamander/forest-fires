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
	final_groupings = {}
	for col in df.columns:
		if col != 'fire_bool': 	
			model_groupings = calc_bins(df, col, num_bins)
			final_groupings[col] = model_groupings

	return final_groupings

def calc_bins(df, col, num_bins): 
	'''
	Input: Pandas DataFrame, Integer
	Output: 2D Numpy Array
	'''

	bin_breaks = np.linspace(0, 1, num_bins + 1)

	fires_dict = defaultdict(list)
	for idx in xrange(num_bins):
		bin_bottom, bin_top = bin_breaks[idx], bin_breaks[idx + 1]
		fires_query = 'fire_bool == 1 and ' + col + ' > ' + str(bin_bottom) + ' and ' + col + ' < ' + str(bin_top)
		non_fires_query = 'fire_bool == 0 and ' + col + ' > ' + str(bin_bottom) + ' and ' + col + ' < ' + str(bin_top)
		fires = df.query(fires_query).count()[col] 
		non_fires = df.query(non_fires_query).count()[col] 
		fires_dict[0].append(non_fires)
		fires_dict[1].append(fires)

	return fires_dict
	

if __name__ == '__main__': 
	df = pd.read_csv('../../data/csvs/model_preds.csv')

	final_groups = output_preds_hist(df)

	with open('model_preds.json', 'w+') as f:
		json.dump(final_groups, f) 
