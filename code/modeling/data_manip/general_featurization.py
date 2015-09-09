import pandas as pd

def grab_columns(df, columns_list): 
	'''
	Input: Pandas DataFrame, List of Strings
	Output: DataFrame

	Return only those columns that we want from the dataframe. 
	'''

	return df[columns_list]

def return_all_dummies(df, col_list): 
	'''
	Input: Pandas DataFrame, List of Strings
	Ouput: Pandas DataFrame

	Take in the list of column names, and for each column, dummy it, merge those dummies back onto the 
	DataFrame, delete the original column (we won't want it in our model anymore), and then output the 
	results. 
	'''

	for col in col_list: 
		dummies = pd.get_dummies(df[col_list])
		df = pd.concat(df, dummies)
		del df[col]

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
