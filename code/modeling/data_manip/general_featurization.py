import pandas as pd
import numpy as np

def return_all_dummies(df, **kwargs): 
	'''
	Input: Pandas DataFrame, Dictionary of Arguments 
	Ouput: Pandas DataFrame
        
        Grab the column that we want to dummy from the 'col' key in **kwargs, 
        and create dummys for every value in that column. 
	'''
        col = kwargs.pop('col', None)
        if col is None: 
            raise RuntimeError('Need to pass a column name to dummy for \
                    return_all_dummies')

	dummies = pd.get_dummies(df[col], prefix=col)
	df = pd.concat([df, dummies], axis=1)
	df = df.drop(col, axis=1)

	return df

def create_new_col(df, **kwargs): 
	'''
	Input: Pandas DataFrame, Dictionary 
	Output: Pandas DataFrame

        Take in the arguments in **kwargs, and create a new column in the data
        frame based off of those arguments. In theory, this column could 
        be created by either an eval statement or a query statement, but 
        for right now I'm just using an eval statement. 
	'''

        eval_string = kwargs.pop('eval_string', None)
        new_column_name = kwargs.pop('new_col_name', None)
        delete_columns = kwargs.pop('delete_columns', False)

        if eval_string is None and new_column_name is None: 
            raise RuntimeError('Need an eval string and column name to create a \
                    column in create_new_col.')

        df[new_column_name] = df.eval(eval_string)
        if delete_columns: 
            df.drop(delete_columns, axis = 1, inplace = True)

	return df

