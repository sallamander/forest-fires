import pandas as pd
import numpy as np
import multiprocessing
import time
from itertools import izip
from datetime import timedelta
from functools import partial 

def gen_nearby_fires_count(df, kwargs):
    '''
    Input: Pandas DataFrame, Float, List
    Output:  Pandas DataFrame

    For each row in the detected fires data set, create a new column that is 
    the count of nearby potential detected fires, as well as a count of the 
    nearby actually detected fires (here we will be look only 1+ days back 
    since we won't have that information for the current day in real time), 
    where nearby detected fires are determined by the inputted dist_measure 
    and time_measures list passed in **kwargs.
    '''

    time_measures = kwargs.pop('time_measures', None)
    dist_measure = kwargs.pop('dist_measure', None)
    quant_test = kwargs.pop('quant_test', False)

    if time_measures is None or dist_measure is None: 
        raise RuntimeError('Inappropriate arguments passed to gen_nearby_fires_count')

    lat_idx, long_idx, date_idx = grab_col_indices(df, ['lat', 'long', 'date_fire'])
    multiprocessing_df = df.drop_duplicates(['lat', 'long', 'date_fire'])
    multiprocessing_df = multiprocessing_df.reset_index(drop=True)
    multiprocessing_df, dt_percentiles_df_dict = add_date_percentiles(multiprocessing_df)
    for time_measure in time_measures: 
        lat_idx, long_idx, date_idx, date_percentile_idx = grab_col_indices(multiprocessing_df, 
                        ['lat', 'long', 'date_fire', 'date_fire_percentiles'])
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        execute_query = partial(query_for_nearby_fires, dt_percentiles_df_dict, 
                                dist_measure, time_measure, lat_idx, long_idx, 
                                date_idx, date_percentile_idx)
        nearby_count_dict = pool.map(execute_query, multiprocessing_df.values) 
        pool.close()
        df = merge_results(df, nearby_count_dict)

    return df

def add_date_percentiles(df): 
    '''
    Input: Pandas DataFrame
    Output: Pandas DataFrame, Dictionary of DataFrames

    For the inputted dataframe, partition the data into 100 equal-sized percentiles
    by date, and add a column holding what percentile each row is in. In addition, 
    output a dictionary that holds 100 key-value pairs, where the key is the percentile
    and the value is a dataframe holding only the observations in that percentile.
    '''

    new_col_name = 'date_fire_percentiles'
    n_quantiles = 100
    df.sort('date_fire', inplace=True) 
    df.reset_index(drop=True, inplace=True)
    step_size = df.shape[0] / n_quantiles
    df['date_fire_percentiles'] = 0

    for quantile in xrange(1, n_quantiles + 1):
        beg_idx = (quantile - 1) * step_size
        end_idx = quantile * step_size
        if quantile == n_quantiles:
            df.loc[beg_idx:, 'date_fire_percentiles'] = quantile 
        else: 
            df.loc[beg_idx:end_idx, 'date_fire_percentiles'] = quantile 
        
    dt_percentiles_df_dict = {}
    for percentile in xrange(1, n_quantiles + 1):
        query = new_col_name + ' == ' + str(percentile)
        dt_percentiles_df_dict[percentile] = df.query(query)

    return df, dt_percentiles_df_dict

def grab_col_indices(df, col_list):
    '''
    Input: Pandas DataFrame, List
    Output: Tuple

    For the inputted dataframe and list of column names, output a tuple of the 
    column indices for those columns. 
    '''

    df_columns = df.columns
    idx_list = [np.where(df_columns == col)[0][0] for col in col_list]

    return tuple(idx_list)

def query_for_nearby_fires(dt_percentiles_df_dict, dist_measure, time_measure, 
                        lat_idx, long_idx, date_idx, date_percentile_idx, row): 
    '''
    Input: Dictionary of DataFrames, Float, Integer, 
            Integer, Integer, Integer, Integer, Numpy Array
    Output: Dictionary 

    For the inputted row, query the dataframe for the number of 
    'detected fires' (i.e. other rows) that are within dist_measure 
    of the inputted row (lat/long wise)  and within the time_measure 
    of the inputted row (date wise). Also query for the number of actual 
    fires (i.e. other rows with fire_bool = True) within the dist_measure
    and time_measure.
    '''
    
    # All the indices are passed in so we can grab the right valuues from the row. 
    # Numpy arrays don't have column names. 
    lat, lng, date = row[lat_idx], row[long_idx], row[date_idx]
    lat_min, lat_max = lat - dist_measure, lat + dist_measure
    long_min, long_max = lng - dist_measure, lng + dist_measure
    row_dt_percentile = row[date_percentile_idx]

    # Note we're not doing day_max here because in real time we wouldn't have forward dates. 
    if time_measure == 0: 
        hour, minute, second = date.hour, date.minute, date.second
        date_min = date - timedelta(hours=hour)
        date_min = date_min - timedelta(minutes=minute)
        date_min = date_min - timedelta(seconds = second)
    else: 
        date_min  = date - timedelta(days=time_measure)
        
    percentile_df = dt_percentiles_df_dict[row_dt_percentile]
    percentile_date_min = percentile_df['date_fire'].min()
    nearby_fires_count = 0
    all_nearby_count = 0
    dt_percentile = row_dt_percentile


    all_nearby_query = '''lat >= @lat_min and lat <= @lat_max and long >= @long_min and long <= @long_max and date_fire >= @date_min and date_fire <= @date'''
    nearby_fires_query = all_nearby_query + " and fire_bool == True" 
    all_nearby_count += percentile_df.query(all_nearby_query).shape[0]
    nearby_fires_count += percentile_df.query(nearby_fires_query).shape[0]
    
    # We're going to query the date percentile of the dataframe that the given row
    # is in, along with the one below and one above (this will ensure we don't 
    # miss any data points). 
    row_dt_percentile -=1
    if row_dt_percentile > 0: 
        percentile_df = dt_percentiles_df_dict[row_dt_percentile]
        all_nearby_count += percentile_df.query(all_nearby_query).shape[0]
        nearby_fires_count += percentile_df.query(nearby_fires_query).shape[0]
    row_dt_percentile += 2
    percentile_df = dt_percentiles_df_dict[row_dt_percentile]
    all_nearby_count += percentile_df.query(all_nearby_query).shape[0]
    nearby_fires_count += percentile_df.query(nearby_fires_query).shape[0]

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
    by lat, long, and date. The nearby_count_dict holds the information 
    calcalated in the query_for_nearby_fires function for each latitude, 
    longitude, and date combo. 
    '''

    nearby_fires_df = pd.DataFrame(nearby_count_dict)
    nearby_fires_df = nearby_fires_df.drop_duplicates()
    df = pd.merge(df, nearby_fires_df, how='inner', on=['lat', 'long', 'date_fire'])

    return df

def gen_rate_nearby_fires(df, time_measure): 
    '''
    Input: Pandas DataFrame, Integer 
    Output DataFrame

    For the inputted time_measure, find the percentage change in the 
    number of fires from the day before to that day. I.e. if the 
    time_measure is 6, then find the percentage change in the 
    number of fires from 7 days prior to 6 days prior. Since these 
    columns are already created in the passed in  df, this will be 
    pretty easy. 
    '''

    today_column = 'nearby_count_' + str(time_measure)
    yesterday_column = 'nearby_count_' + str(time_measure + 1)
    new_col_name = 'perc_change_' + str(time_measure) + '_' + str(time_measure + 1)
    df[new_col_name] = (df[today_column] - df[yesterday_column]) / df[yesterday_column]

    return df
