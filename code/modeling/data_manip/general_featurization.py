import pandas as pd

def grab_columns(df, columns_list): 
	'''
	Input: Pandas DataFrame, List of Strings
	Output: DataFrame

	Return only those columns that we want from the dataframe. 
	'''

	return df[columns_list]

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

def combine_dfs(df_list): 
	'''
	Input: List of Pandas DataFrame
	Output: Pandas DataFrame

	Combine each of the pandas dataframes in the df_list into one single dataframe. Note that I'm assuming 
	that they have the same column names. 
	'''

	output_df = df_list[0]

	if len(df_list) == 1: 
		return output_df
	else: 
		for df in df_list[1:]: 
			output_df = output_df.append(df)
		return output_df

def boolean_col(df, col, val_dict): 
	'''
	Input: Pandas DataFrame, String, Dictionary
	Output: Pandas DataFrame

	Rework the fire variable from strings ('t', 'f') to a boolean to predict off of (True, False).
	'''

	df = df.replace({col: {'f': 0, 't': 1}})
	return df
