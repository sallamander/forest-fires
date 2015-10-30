import pandas as pd
import numpy as np

def return_all_dummies(df, col, val_dict): 
	'''
	Input: Pandas DataFrame, String, Dictionary
	Ouput: Pandas DataFrame

	Take in the column name, and for that column, dummy it, merge those dummies back onto the 
	DataFrame, delete the original column (we won't want it in our model anymore), and then output the 
	results. 
	'''

	dummies = pd.get_dummies(df[col])
	for dummy_col in dummies.columns:
		dummies.rename(columns={dummy_col: col + '_' + dummy_col}, inplace=True) 
	df = pd.concat([df, dummies], axis=1)
	df = df.drop(col, axis=1)

	return df

def return_top_n(df, col, val_dict): 
	'''
	Input: Pandas DataFrame, String, Dictionary
	Output: Pandas DataFrame

	For the column inputted, take it and dummy it, and then the top n observations, measured by 
	some groupby metric around the new column created (for example, the absolute difference between 
	the fire boolean and confidence). 
	'''
	n = val_dict['n']
	manip_type = val_dict['manip_type']
	dummies = pd.get_dummies(df[col])

	if manip_type == 'eval': 
		new_col = val_dict['new_col']
		df[new_col] = df.eval(val_dict['eval_string'])
		df[new_col] = abs(df[new_col])
		dummies_count = df.groupby(col).sum()[new_col]
		df.drop(new_col, axis=1, inplace=True)

	names = dummies_count.nlargest(n).index	

	for dummy_col in names: 
		df[dummy_col] = dummies[dummy_col]

	df = df.drop(col, axis=1)	
	return df

def boolean_col(df, col, val_dict): 
	'''
	Input: Pandas DataFrame, String, Dictionary
	Output: Pandas DataFrame

	Rework the fire variable from strings ('t', 'f') to a boolean to predict off of (True, False).
	'''

	df = df.replace({col: {'f': 0, 't': 1}})
	return df

def create_new_col(df, col, val_dict): 
	'''
	Input: Pandas DataFrame, String, Dictionary
	Output: Pandas DataFrame

	Take in the pandas data frame, and create a new col via the specifications of the val_dict. This is a little
	different than functions above - the col coming in will be the name of the new column to create. The key/value 
	pairs in the val_dict will tell us how to create that column. 

	'''

	eval_string = val_dict['eval_string']

	df[col] = df.eval(eval_string)

	val_dict_keys = val_dict.keys()

	if 'delete_columns' in val_dict_keys: 
		for del_col in val_dict['delete_columns']: 
			df.drop(del_col, axis=1, inplace=True)
	if 'replace_nulls' in val_dict_keys: 
		df.fillna(-9999, inplace=True)
		df.replace([np.inf, -np.inf], np.nan, inplace=True)
		df.fillna(-99999, inplace=True)

	return df

def return_outlier_boolean(df, col, val_dict): 
	'''
	Input: Pandas DataFrame, String, Dictionary
	Output: Pandas DataFrame

	Take in the pandas dataframe, and for the given col, create a boolean for whether or not each row is 
	an outlier for that given column, where outlier will be determined by the val_dict key/value pairs. 
	'''
	col_values = df[col].values
	col_mean, col_std = np.mean(col_values), np.std(col_values)

	new_col_name = col + '_outlier_bool'
	std_multiplier = val_dict['std_multiplier']
	eval_string = col + ' < (@col_mean - @std_multiplier * @col_std) or ' + col + ' > (@col_mean + @std_multiplier * @col_std)' 
	
	df[new_col_name] = df.eval(eval_string)
	df.drop(col, axis=1, inplace=True)

	return df

