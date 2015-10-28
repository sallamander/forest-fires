import pandas as pd
import numpy as np
import time
from itertools import izip
from datetime import datetime, timedelta

def add_date_column(df):
    '''
    Input: Pandas DataFrame
    Output Pandas DataFrame
    '''
        
    df['date_fire']=[datetime.strptime(date + "-" + str(gmt), "%Y-%m-%d-%H%M") for \
                    date, gmt in izip(df['date'].values, df['gmt'].values)]

    return df

def insert_quantile_col(df, col, n_quantiles): 
    '''
    Input: Pandas DataFrame, String, Integer 
    Output: Pandas DataFrame

    For the column denoted by col, create a new column in the inputted df 
    that holds the quantile number for where each row falls in the inputted col.
    Use n_quantiles numbers of quantiles. 
    '''
    new_col_name = col + '_quantiles'
    
    if col == 'date_fire':
        df['date_fire2'] = df[col].apply(lambda x: x.toordinal())
        col = 'date_fire2'

    df[new_col_name] = pd.qcut(df[col].values, n_quantiles, labels=False)

    if col=='date_fire2': 
        del df[col] 

    return df

def nearby_fires_count(row, default=False):
    '''
    Input: Numpy Array, Boolean
    Output: Dictionary

    For the given row, query for nearby fires, as denoted by the global dist_measure
    and time_measure. The one caveat here, though, is that we want to query only 
    in those quantile groups of lat, long, and date that are directly around our 
    row. So if our row is in quantile 1 for lat, only query quantiles 0 and 2 in 
    terms of lat. If it's in quantile 5 for long, only query quantiles 4 and 6 for long. 
    '''
    
    lat, lng, date = row[lat_idx], row[lng_idx], row[dt_idx]
    lat_quantile, long_quantile, date_quantile = row[lat_qidx], row[long_qidx], \
                                                 row[date_qidx]
    lat_q_min, lat_q_max = lat_quantile - 1, lat_quantile + 1
    long_q_min, long_q_max = long_quantile - 1, long_quantile + 1
    date_q_min, date_q_max = date_quantile - 1, date_quantile + 1

    lat_min, lat_max = lat - dist_measure2, lat + dist_measure2
    long_min, long_max = lng - dist_measure2, lng + dist_measure2
    date_min  = date - timedelta(days=time_measure2)
    
    query1 = '''lat_quantiles >= @lat_q_min and lat_quantiles <= @lat_q_max and long_quantiles >= @long_q_min and long_quantiles <= @long_q_max and date_fire_quantiles >= @date_q_min and date_fire_quantiles <= @date_q_max'''
    query2 = '''lat >= @lat_min and lat <= @lat_max and long >= @long_min and long <= @long_max and date_fire >= @date_min and date_fire <= @date'''

    if default: 
        nearby_count = df2.query(query2).shape[0]
    else: 
        nearby_count = df2.query(query1).query(query2).shape[0]
    
    nearby_count_label = 'nearby_count_' + str(time_measure2)	

    output_dict = {'lat': lat, 'long': lng, 'date_count': date, 
                    nearby_count_label: nearby_count}

    return output_dict

def query_prep_clean(df, dist_measure, time_measure, beginning=True): 
    '''
    Input: Pandas DataFrame, Float, Float, Boolean
    Output: Global Variables (deleted or created)

    For the inputted dataframe and time dist measure, create the necessary global 
    variables for the multiprocessing environment. Since I am multiprocessing 
    a dataframe query, I need to be able to either pass the dataframe through 
    the multiprocessing pool, or make it a global. While neither is ideal, the 
    second seems better. I'll make sure to delete the global when I'm all done. 
    '''

    if beginning == True: 
            global df2, lat_idx, lng_idx, dt_idx, dist_measure2, time_measure2, \
                    lat_qidx, long_qidx, date_qidx
            dist_measure2, time_measure2 = dist_measure, time_measure
            df2 = df.copy()
            df_columns = df2.columns
            lat_idx, lng_idx, dt_idx = np.where(df_columns == 'lat')[0][0], \
                                        np.where(df_columns == 'long')[0][0], \
                                        np.where(df_columns == 'date_fire')[0][0] 
            lat_qidx, long_qidx, date_qidx = \
                    np.where(df_columns == 'lat_quantiles')[0][0], \
                    np.where(df_columns == 'long_quantiles')[0][0], \
                    np.where(df_columns == 'date_fire_quantiles')[0][0]

    if beginning == False:
            del df2, lat_idx, lng_idx, dt_idx, dist_measure2, time_measure2, \
                    lat_quantile, long_quantile, date_quantile

def grab_nearby(df, dist_measure, time_measure, default): 
    '''
    Input: Pandas DataFrame, Float, Integer
    Output: Pandas DataFrame 

    Grab nearby fires, as defined by being within +/- the distance measure and 
    +/- the time measure of the current rows lat, long coordinates, and 
    date_fire. 
    '''
    
    query_prep_clean(df, dist_measure, time_measure, beginning = True) 
    nearby_count_dicts = [nearby_fires_count(row, default=default) for row in df2.values[0:100]]

    return nearby_count_dicts

if __name__ == '__main__': 
    full_df = pd.DataFrame()
    for idx, year in enumerate(xrange(2012, 2016)): 
        df = pd.read_csv('../../../data/csvs/detected_fires_{}.csv'.format(str(year)))
        if idx == 0: 
            full_df = df
        else: 
            full_df = full_df.append(df)

    full_df = add_date_column(full_df)   
    num_quantiles = 10
    for col in ['lat', 'long', 'date_fire']: 
        full_df = insert_quantile_col(full_df, col, num_quantiles)
    time_start = time.time()
    for i in xrange(100): 
        result = grab_nearby(full_df, dist_measure=0.1, time_measure = 1, default=True)
    time_end = time.time()

    print 'time_run_default:', (time_end - time_start)

    time_start = time.time()
    for i in xrange(100): 
        result2 = grab_nearby(full_df, dist_measure=0.1, time_measure = 1, default=False)
    time_end = time.time()

    print 'time_run_new:', (time_end - time_start)
