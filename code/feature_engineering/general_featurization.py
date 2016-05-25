"""A module for basic data processing tasks. 

This module contains general, fairly standard functions that can be run in data 
processing tasks. This includes one for creating dummy variables 
(`return_all_dummies`) and one for creating a new column based on an `eval` 
string (`create_new_col`). These are the only two meant to be called externally 
from the module (`_add_date_col` is simply a helper function). 

In the first two functions mentioned above, there is a use of a kwargs argument 
in a somewhat non-traditional way. This has to do with how the `create_inputs.py` 
module calls the functions. To allow for flexibility in the function calls in the 
`create_inputs.py` module, a somewhat non-traditional use of kwargs helped. 
"""

import pandas as pd
import numpy as np

def return_all_dummies(df, kwargs): 
    """Create dummy variables for an inputted column. 

    Grab the column to dummy from the `col` key in **kwargs, create dummies for 
    every value in that column, and concat those onto the inputted DataFrame. 

    Args: 
    ----
        df: Pandas DataFrame 
        kwargs: dct
            Holds arguments to use in the function. Here we expect the `col` 
            keyword to be passed in. See the module docstring for an explanation 
            of the use of kwargs here. 

    Return: 
    ------
        df: Pandas DataFrame
    """

    col = kwargs.pop('col', None)
    if col is None: 
        raise RuntimeError('Need to pass a column name to dummy for \
                return_all_dummies')

    # For both year and month, these are only implicitly in the df via the date 
    # column. We need to explicity add them to dummy them. 
    if col in ['year', 'month']: 
        df = _add_date_col(df, col)	

    dummies = pd.get_dummies(df[col], prefix=col)
    df = pd.concat([df, dummies], axis=1)
    df = df.drop(col, axis=1)

    return df

def create_new_col(df, kwargs): 
    """Create a new column in the df based off the inputted specifications. 

    Create a new column in the df based off an inputted `eval` statement passed 
    in `kwargs`. Name the column the inputted `new_col_name` passed in `kwargs`. 

    Args: 
    ----
        df: Pandas DataFrame 
        kwargs: dct
            Holds optional arguments to use in the function. Here we expect the 
            `eval_string` and `new_col_name` arguments to be passed in. See the 
            module docstring for an explanation of the use of kwargs here. 

    Return: 
    ------
        df: Pandas DataFrame
    """
	
    eval_string = kwargs.pop('eval_string', None)
    new_column_name = kwargs.pop('new_col_name', None)
    delete_columns = kwargs.pop('delete_columns', False)

    if eval_string is None or new_column_name is None: 
        raise RuntimeError('Need an eval string and column name to create a \
                column in create_new_col.')

    df[new_column_name] = df.eval(eval_string)
    if delete_columns: 
        df.drop(delete_columns, axis = 1, inplace = True)

    return df

def _add_date_col(df, col_name): 
    """Create a new date-based column in the inputted DataFrame. 

    Add either a year or month column into the `df`, using the `date_fire` 
    column to do so. This is meant to be a helper function to `return_all_dummies`. 

    Args: 
    ----
        df: Pandas DataFrame
        col_name: str 
            Denotes the new column name to create, and holds the time
            denomination to input into the column.

    Return: 
    ------
        df: Pandas DataFrame
    """

    if col_name == 'year': 
        df[col_name] = [dt.year for dt in df['date_fire']]
    if col_name == 'month': 
        df[col_name] = [dt.month for dt in df['date_fire']]

    return df

