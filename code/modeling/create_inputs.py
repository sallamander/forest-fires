import pandas as pd
import sys
import pickle
import time
from data_manip.general_featurization import return_all_dummies, create_new_col
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

    filepath = '../data/csvs/detected_fires_' + str(year) + '.csv'
    df = pd.read_csv(filepath, true_values = ['t'], false_values=['f'])

    return df

if __name__ == '__main__': 
    with open('makefiles/year_list.pkl') as f: 
        year_list = pickle.load(f)
    
    # Assume that we haven't done the geography transformation unless we 
    # explicity tell it. This option is here because gen_nearby_fires_count
    # takes a long time to run; so we want the option to bypass it.
    if len(sys.argv) >= 1: 
        geo = True if 'geo' in sys.argv else False
        time = True if 'time' in sys.argv else False

    # We'll create a dictionary that will hold all the transformations we'll 
    # peform on our data; then we can access the function we'll use to transform 
    # our data by the key of the dictionary. 
    featurization_dict = {'all_dummies': return_all_dummies, 
                            'create_new_col': create_new_col, 
                            'add_nearby_fires': gen_nearby_fires_count
                         }
     
    if geo: 
        with open('makefiles/geo_transforms_dict.pkl') as f: 
            geo_transforms_dict = pickle.load(f)
        dfs_list = [get_df(year) for year in year_list] 
        df = pd.concat(dfs_list, ignore_index=True)
        df = add_date_column(df)
        for k, v in geo_transforms_dict.iteritems(): 
            df = featurization_dict[v['transformation']](df, v)
    '''
    else: 
        df = pd.read_csv('geo_done.csv')
        with open('makefiles/time_transforms_dict.pkl') as f:
            time_transforms_dict = pickle.load(f)
        for k, v in time_transforms_dict.iteritems(): 
            df = featurization_dict[v['transformation']](df, v)

   ''' 
