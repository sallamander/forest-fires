import pandas as pd
import numpy as np
import multiprocessing
from itertools import izip
from datetime import timedelta
from functools import partial 

def gen_nearby_fires_count(df, dist_measure, time_measures):
    '''
    Input: Pandas DataFrame, Float, List
    Output:  Pandas DataFrame

    For each row in the detected fires data set, create a new column that is 
    the count of nearby potential detected fires, as well as a count of the 
    nearby actually detected fires (here we will be look only 1+ days back 
    since we won't have that information for the current day in real time), 
    where nearby detected fires are determined by the inputted dist_measure 
    and time_measures list.  
    '''
    lat_idx, long_idx, date_idx = grab_col_indices(df, ['lat', 'long', 'date_fire'])
    df = df.drop_duplicates(['lat', 'long', 'date_fire'])
    for time_measure in time_measures: 
        pool = multiprocessing.Pool(3)
        execute_query = partial(query_for_nearby_fires, df, 
                                dist_measure, time_measure, lat_idx, 
                                long_idx, date_idx)
        nearby_count_dict = pool.map(execute_query, df.values[0:100]) 
        df = merge_results(df, nearby_count_dict)

    return df

def query_for_nearby_fires(df, dist_measure, time_measure, 
                        lat_idx, long_idx, date_idx, row): 
    '''
    Input: Numpy Array, Pandas DataFrame, Numpy Array, Float, Integer, 
            Integer, Integer, Integer
    Output: Dictionary 

    For the inputted row, query the dataframe for the number of 
    'detected fires' (i.e. other rows) that are within dist_measure 
    of the inputted row (lat/long wise)  and within the time_measure 
    of the inputted row (date wise). 
    '''
    lat, lng, date = row[lat_idx], row[long_idx], row[date_idx]
    lat_min, lat_max = lat - dist_measure, lat + dist_measure
    long_min, long_max = lng - dist_measure, lng + dist_measure

    # Note we're not doing day_max here because in real time we wouldn't have forward dates. 
    if time_measure == 0: 
        hour, minute, second = date.hour, date.minute, date.second
        date_min = date - timedelta(hours=hour)
        date_min = date_min - timedelta(minutes=minute)
        date_min = date_min - timedelta(seconds = second)
    else: 
        date_min  = date - timedelta(days=time_measure)

    all_nearby_query = '''lat >= @lat_min and lat <= @lat_max and long >= @long_min and long <= @long_max and date_fire >= @date_min and date_fire <= @date'''
    nearby_fires_query = all_nearby_query + " and fire_bool == True" 
    all_nearby_count = df.query(all_nearby_query).shape[0]
    nearby_fires_count = df.query(nearby_fires_query).shape[0]

    all_nearby_count_label = 'all_nearby_count' + str(time_measure)	
    nearby_fires_count_label = 'all_nearby_fires' + str(time_measure)	
    output_dict = {'lat': lat, 'long': lng, 'date_fire': date, 
                    all_nearby_count_label: all_nearby_count, 
                    nearby_fires_count_label: nearby_fires_count}

    return output_dict

def merge_results(df, nearby_count_dict): 
    '''
    Input: Pandas DataFrame, Dictionary
    Output: Pandas DataFrame

    Take in the nearby_count_dict, and merge it into the current df 
    we are working with to run it through the model. We will be merging 
    by lat, long, and date. 
    '''

    nearby_fires_df = pd.DataFrame(nearby_count_dict)
    nearby_fires_df = nearby_fires_df.drop_duplicates()
    df = pd.merge(df, nearby_fires_df, how='inner', on=['lat', 'long', 'date_fire'])

    return df

def grab_col_indices(df, col_list):
    '''
    Input: Pandas DataFrame
    Output: Tuple

    For the inputted dataframe and list of column names, output a tuple of the 
    column indices for those columns. 
    '''

    df_columns = df.columns
    idx_list = [np.where(df_columns == col)[0][0] for col in col_list]

    return tuple(idx_list)

def gen_rate_nearby_fires(df, time_measure): 
    '''
    Input: Pandas DataFrame, Integer 
    Output DataFrame

    For the inputted time_measure, find the percentage change in the 
    number of fires from the day before to that day. I.e. if the 
    time_measure is 6, then find the percentage change in the 
    number of fires from 7 days prior to 6 days prior. Since these 
    columns are already created in the df, this will be pretty easy. 
    '''

    today_column = 'nearby_count_' + str(time_measure)
    yesterday_column = 'nearby_count_' + str(time_measure + 1)
    new_col_name = 'perc_change_' + str(time_measure) + '_' + str(time_measure + 1)
    df[new_col_name] = (df[today_column] - df[yesterday_column]) / df[yesterday_column]

    return df
