"""A tiny module for adding a date column to a DataFrame. 

This module just contains a quick one-off function for adding a date column to 
a DataFrame in one speific use case.
"""

from itertools import izip
from datetime import datetime

def add_date_column(df):
    """Add a date column into the DataFrame. 

    The inputted DataFrame contains the daily date (e.g. 2015-08-03) as well as
    gmt column, that when combined given a timestamp. This function combines those
    two into one `date_fire` column. 

    Args: 
    ----
        df: Pandas DataFrame

    Return: 
    ------
        df: Pandas DataFrame 
    """
        
    df['date_fire']=[datetime.strptime(date + "-" + str(gmt), "%Y-%m-%d-%H%M") for \
                    date, gmt in izip(df['date'].values, df['gmt'].values)]

    return df


