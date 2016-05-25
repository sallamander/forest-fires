"""A module used to drive the feature engineering/data processing process. 

This module drives the feature engineering/data processing process by calling 
other functions from other modules. It's only function is one that is simply 
used to load in all the data before performing feature engineering/data 
processing. 
"""

import pandas as pd
import sys
import pickle
from general_featurization import return_all_dummies, create_new_col
from time_featurization import add_date_column
from geo_featurization import gen_nearby_fires_count, calc_perc_fires

def get_df(year): 
    """Read a year of data into a Dataframe and return it. 

    Args: 
    ----
        year: int
    
    Return: 
    ------
        df: Pandas Dataframe
    """

    filepath = 'data/csvs/detected_fires_MODIS_' + str(year) + '.csv'
    df = pd.read_csv(filepath, true_values = ['t'], false_values=['f'], index_col=False)

    return df

if __name__ == '__main__': 
    try: 
	with open('code/makefiles/year_list.pkl') as f: 
	    year_list = pickle.load(f)
    except IOError: 
	print """Make sure that you have run make_year_list.py in \
		code/makefiles in order to create the year_list.pkl.""".replace('\t', '')
    
    # Assume that we haven't done any of the transformations unless we explicity tell it. 
    # geo = True will lead to geo. transformations being done, and time_bool = True will 
    # lead to time transformations being done 
    if len(sys.argv) >= 1: 
        geo = True if 'geo' in sys.argv else False
        time_bool = True if 'time' in sys.argv else False

    # Create a dictionary that will hold all the transformations we'll peform on 
    # our data (key is the transformation and value is the function to apply). 
    featurization_dict = {'all_dummies': return_all_dummies, 
                            'create_new_col': create_new_col, 
                            'add_nearby_fires': gen_nearby_fires_count
                         }

    if geo: 
        try: 
            with open('code/makefiles/geo_transforms_dict.pkl') as f: 
                geo_transforms_dict = pickle.load(f)
        except IOError: 
            print "Make sure that you have run make_columns_dict.py in \
                    code/makefiles in order to create the \
                    geo_transforms_dict.pkl".format('\t', '')
        
        dfs_list = [get_df(year) for year in year_list] 
        df = pd.concat(dfs_list, ignore_index=True)
        df = add_date_column(df)
        # Drop all observations that are in Canada (denoted by having a missing 
        # value for any of the state/county info.)
        df.dropna(axis=0, subset=['state_name'], inplace=True)
        # Grab this before popping it in the function calls below. 
        time_measures = geo_transforms_dict['add_nearby_fires']['time_measures']
        for k, v in geo_transforms_dict.iteritems(): 
            df = featurization_dict[v['transformation']](df, v)
        df = calc_perc_fires(df, time_measures) 
        df.to_csv('code/modeling/model_input/geo_done.csv', index=False)

    if time_bool: 
        try:
            df = pd.read_csv('code/modeling/model_input/geo_done.csv', 
                    parse_dates=['date_fire'], index_col=False)
        except FileNotFoundError: 
            print "You need to run create_inputs with the geo flag either \
                    before or in conjuction with the time flag".format('\t', '')
        try: 
            with open('code/makefiles/time_transforms_dict.pkl') as f:
                time_transforms_dict = pickle.load(f)
        except IOError: 
            print "Make sure that you have run make_columns_dict.py in \
                    code/makefiles in order to create the \
                    time_transforms_dict.pkl".format('\t', '')

        for k, v in time_transforms_dict.iteritems(): 
            df = featurization_dict[v['transformation']](df, v)

        df.to_csv('code/modeling/model_input/geo_time_done.csv', index=False)


