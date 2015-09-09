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