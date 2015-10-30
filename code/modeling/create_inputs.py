import pandas as pd
import sys
import pickle

from data_manip.general_featurization import return_all_dummies, boolean_col, \
                return_top_n, create_new_col, return_outlier_boolean
from data_manip.time_featurization import add_date_column
from data_manip.geo_featurization import gen_nearby_fires_count

def get_df(year): 
    '''
    Input: Integer
    Output: Pandas Dataframe 

    For the given year, read in the detected fires csv to a pandas dataframe, 
    and output it. This function was written just to make the code a little more 
    readable.
    '''

    filepath = '../../data/csvs/detected_fires_' + str(year) + '.csv'
    df = pd.read_csv(filepath, true_values = ['t'], false_values=['f'])

    return df

if __name__ == '__main__': 
    year_list = [2012, 2013, 2014, 2015]    
    dfs_list = [get_df(year) for year in year_list] 
    df = pd.concat(dfs_list)
    df = add_date_column(df) 
    df = gen_nearby_fires_count(df, 0.01, [0, 1, 2, 3, 4, 5, 6, 7])

    df = grab_columns(df, columns_list)
    featurization_dict = {'all_dummies': return_all_dummies, 'bool_col': boolean_col, 'return_top_n': return_top_n, 
                                            'create_new_col': create_new_col, 'outlier_boolean': return_outlier_boolean}

    for k, v in columns_dict.iteritems(): 
            if k != 'add_nearby_fires' and k!= 'nearby_fires_done':
                    df = featurization_dict[v['transformation']](df, k, v)
    
    input_df_filename = './modeling/input_df_' + str(columns_dict['add_nearby_fires']['dist_measure']) + '.pkl'
    with open(input_df_filename, 'w+') as f: 
            pickle.dump(df, f)
    '''
