"""A module for looking for nearby obs. in lat/long and time space. 

This module uses a driver function in conjunction with 
multiprocessing to find observations in a DataFrame that 
are within a certain distance and time interval from a 
given observation. Distance is defined as plus/minus some 
number in lat/long space, and a time interval is given as 
anything that `datetime.timedelta` allows (minutes, hours, 
weeks, days, etc.). It also allows for other specifications on those 
"nearby" observations (e.g. are they labeled as forest-fires,
in this use case). 

The only function that is meant to be called externally in 
this module is the driver function - `gen_nearby_fires_count`. 
In this function, there is a use of the kwargs argument in
a somewhat non-tradition way. This has to do with how the 
`create_inputs.py` module calls this function. To allow for 
flexibility in the function calls in the `create_inputs.py` 
module, a somewhat non-traditional use of kwargs helped. 
"""

import pandas as pd
import numpy as np
import multiprocessing
import time
from itertools import izip
from datetime import timedelta, datetime
from functools import partial 

def gen_nearby_fires_count(df, kwargs):
    """Count nearby fires/non-fires in lat/long and time space. 

    For each row in the detected fires data set, create a bunch of 
    new columns: 
        
        * One holding the count of nearby detected fires (regardless
          of whether they are labeled as a forest fire), going 
          back 1-7 days 
        * One holding the count of nearby detected fires that are 
          labeled as forest-fires (fire_bool = True), going back 1-7 
          days
        * One holding the count of nearby detected fires that are 
          labeled as forest-fires (fire_bool = True), going back 
          1, 2, and 3 years 

    Nearby will be denoted by +/- some number in lat/long space. 

    This function will just act as a driver for this entire process, 
    and as the function that is meant to be called external from this 
    module. It will drive by calling all of the other helper functions
    in this module (each of which will give a detailed description of 
    what they are doing). It will also multiprocess this across all 
    available cores be default. 

    Args: 
    ----
        df: Pandas DataFrame 
        kwargs: dct
            Holds arguments to use in the function. Here we expect
            the 'time_measures' and 'dist_measure' to keywords 
            to be passed in. See the module docstring for an 
            explanation of the kwargs variable here. 
        
    Return: 
    ------
        df: Pandas DataFrame 
    """

    time_measures = kwargs.pop('time_measures', None)
    dist_measure = kwargs.pop('dist_measure', None)

    if time_measures is None or dist_measure is None: 
        raise RuntimeError('Inappropriate arguments passed to gen_nearby_fires_count')

    # Only keeping the columns I need will keep the df lightweight. 
    keep_cols = ['lat', 'long', 'date_fire', 'fire_bool']
    multiprocessing_df = df[keep_cols] 
    multiprocessing_df, dt_percentiles_df_dict = \
            _prep_multiprocessing(multiprocessing_df)
    col_lst = ['lat', 'long', 'date_fire', 'date_fire_percentiles']
    lat_idx, long_idx, date_idx, date_pctile_idx = \
            _grab_col_indices(multiprocessing_df, col_lst)

    for time_measure in time_measures: 
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        execute_query = partial(query_for_nearby_fires, dt_percentiles_df_dict, 
                                dist_measure, time_measure, lat_idx, long_idx, 
                                date_idx, date_pctile_idx)
        nearby_count_dicts = pool.map(execute_query, 
                multiprocessing_df.values) 
        pool.close()
        df = _merge_results(df, nearby_count_dicts)

    return df

def _prep_multiprocessing(df): 
    """Clean up the inputted df and prepare everything for multiprocessing. 
    
    For multiprocessing, the df needs to be as lightweight as possible. 
    This means dropping any duplicate observations in terms of lat/long
    coordinates and date. We also don't want to count any duplicate 
    observations like this towards the overall count of nearby fires/obs.
    This is the step in this function. 

    The second step involves prepping everything for multiprocessing. The
    quickest/most efficient method found to multiprocess this was the 
    following: 

        * Create a percentile column in the DF corresponding to date
        * Create a dictionary lookup for all rows in a corresponding
          date percentile. This allows us smarter, more efficient 
          querying (e.g. it's only necessary to query the nearby
          percentiles, and not every one). 

    This is a helper function called from `gen_nearby_fires_count`. 

    Args: 
    ----
        df: Pandas DataFrame

    Return: 
    ------
        multiprocessing_df: Pandas DataFrame
            Holds the modified DataFrame, with duplicates dropped and 
            the date percentile column added. 
        dt_percentiles_df_dict: dct of DataFrames 
            Holds the dictionary lookup for all rows in a corresponding 
            date percentile. The key corresponds to the date percentile, 
            and the value corresponds to a DataFrame of all rows in 
            that date percentile. 
    """

    multiprocessing_df = df.drop_duplicates(['lat', 'long', 'date_fire'])
    multiprocessing_df = multiprocessing_df.reset_index(drop=True)
    multiprocessing_df, dt_percentiles_df_dict = \
            _handle_date_percentiles(multiprocessing_df)

    return multiprocessing_df, dt_percentiles_df_dict 

def _handle_date_percentiles(df): 
    """Add a column of the date percentile and output dictionary lookup. 

    For the inputted DataFrame, partition the data into 100 equal-sized 
    percentiles by date, and add a column holding what percentile each 
    row is in. In addition, output a dictionary that holds 100 key-value 
    pairs, where the key is the percentile and the value is a DataFrame 
    holding only the observations in that percentile.

    This is a helper function called from `_prep_multiprocessing`, and 
    itself calls helper functions `_setup_percentiles_column` and 
    `_setup_pctiles_df_dct`. 

    Args: 
    ----
        df: Pandas DataFrame

    Return: 
    ------
        df: Pandas DataFrame
            Holds the modified DataFrame, with the date percentile 
            column added. 
        dt_percentiles_df_dict: dct of DataFrames 
            Holds the dictionary lookup for all rows in a corresponding 
            date percentile. The key corresponds to the date percentile, 
            and the value corresponds to a DataFrame of all rows in 
            that date percentile. 
    """

    new_col_name = 'date_fire_percentiles'
    n_quantiles = 100
    df.sort('date_fire', inplace=True) 
    df.reset_index(drop=True, inplace=True)
    step_size = df.shape[0] / n_quantiles
    df[new_col_name] = 0

    df = _setup_pctiles_column(df, step_size, n_quantiles, new_col_name)
    dt_percentiles_df_dct = _setup_pctiles_df_dct(df, n_quantiles, new_col_name)

    return df, dt_percentiles_df_dct

def _setup_pctiles_column(df, step_size, n_quantiles, new_col_name): 
    """Create the `date_fire_percentiles` column for the df. 

    For each row in the dataframe, figure out what percentile of the date 
    column it is in, and input that into the 'date_fire_percentiles' column
    of the dataframe. 

    This is a helper function called from `_handle_date_percentiles`. 

    Args: 
    ----
        df: Pandas DataFrame
        step_size: int
            Holds the number of observations to step through by 
            to get to the next percentile/bin. 
        n_quantiles: int
            Holds the number of percentiles/bins to make.
        new_col_name: str
            Holds the name to give the newly created column. 

    Return: 
    ------
        df: Pandas DataFrame  
    """

    for quantile in xrange(1, n_quantiles + 1):
        beg_idx = (quantile - 1) * step_size
        end_idx = quantile * step_size
        if quantile == n_quantiles:
            df.loc[beg_idx:, new_col_name] = quantile 
        else: 
            df.loc[beg_idx:end_idx, new_col_name] = quantile 

    return df

def _setup_pctiles_df_dct(df, n_quantiles, new_col_name): 
    """Create a lookup dictionary for rows of the DataFrame by date percentile.  

    Create a dictionary of DataFrames, where the keys are the integers 
    corresponding to percentile of the date column an ob. is in, and 
    the values are Pandas DataFrames holding all the obs. in that percentile. 

    This is a helper function called from `_handle_date_percentiles`. 

    Args: 
    ----
        df: Pandas DataFrame
        n_quantiles: int
            Holds how many quantiles/bins the date column was broken into. 
        new_col_name: str

    Returns: 
    -------
        dt_percentiles_df_dict: dct of DataFrames
            Holds the lookup dictionary. 
    """

    dt_percentiles_df_dict = {}
    for percentile in xrange(1, n_quantiles + 1):
        query = new_col_name + ' == ' + str(percentile)
        dt_percentiles_df_dict[percentile] = df.query(query)

    return dt_percentiles_df_dict

def _grab_col_indices(df, col_list):
    """Output a tuple of the column indices for the inputted column names. 

    This is a helper function called from `gen_nearby_fires_count`. It 
    allows the passing of integers to reference the correct "columns" 
    of the numpy array passed during multiprocessing. 

    Args: 
    ----
        df: Pandas DataFrame 
        col_list: list of strings 
            Holds the column names to grab the indices of. 

    Return: 
    ------
        tuple 
    """

    df_columns = df.columns
    idx_list = [np.where(df_columns == col)[0][0] for col in col_list]

    return tuple(idx_list)

def query_for_nearby_fires(dt_percentiles_df_dict, dist_measure, time_measure, 
                        lat_idx, long_idx, date_idx, date_percentile_idx, row): 
    """Query the DataFrame for the nearby obs/fires. 
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

    This is a helper function called and multiprocessed from 
    `gen_nearby_fires_count`. 

    Args: 
    ----
        dt_percentiles_df_dict: dct of DataFrames 
            Holds the key-value pairs corresponding to date 
            percentile and rows of a DataFrame in that percentile. 
        dist_measure: float
            Holds how far to look in lat/long space for "nearby" obs. 
        time_measure: int
            Holds how far back in time to look for "nearby" obs. 
        lat_idx: int
            Holds the column index of the latitude value in the inputted row. 
        long_idx: int
            Holds the column index of the longitude value in the inputted row. 
        date_idx: int
            Holds the column index of the date value in the inputted row. 
        date_percentile_idx: int
            Holds the date percentile the inputted row is in. 
        row: numpy.ndarray
            Holds all info for the current observation. 

    Return: 
    ------
        output_dict: dct
            Holds key-value pairs for all of the info. that was 
            queried for. 
    """
    
    # All the indices are passed in so we can grab the right values from the row. 
    # Numpy arrays don't have column names. 
    lat, lng, date = row[lat_idx], row[long_idx], row[date_idx]
    lat_min, lat_max, long_min, long_max = \
            _get_lat_long_range(lat, lng, dist_measure)
    row_dt_percentile = row[date_percentile_idx]

    date_min, date_max = _get_date_range(time_measure, date)

    percentile_df = dt_percentiles_df_dict[row_dt_percentile]
    percentile_date_min = percentile_df['date_fire'].min()
    nearby_fires_count = 0
    all_nearby_count = 0

    all_nearby_query = '''lat >= @lat_min and lat <= @lat_max and long >= @long_min and long <= @long_max and date_fire >= @date_min and date_fire <= @date'''
    # In real time we won't know which rows are actually fires (fire_bool == True)
    # on the day of; we have to wait until after business hours when the 
    # fire perimter boundaries are posted. 
    nearby_fires_query = '''lat >= @lat_min and lat <= @lat_max and long >= @long_min and long <= @long_max and date_fire >= @date_min and date_fire < @date_max and fire_bool == True'''
    all_nearby_count += percentile_df.query(all_nearby_query).shape[0]
    nearby_fires_count += percentile_df.query(nearby_fires_query).shape[0]
   
    # If we're doing 1-7 days, we're going to query the date percentile that 
    # the given row is in, as well as the above and below. If we're going 
    # more days back, it'll be years back, and we'll want to add in all 
    # percentiles below (not just the one directly below). 
    min_dt_percentile = 1 if time_measure > 7 else \
        max(row_dt_percentile - 1, 1)
    max_dt_percentile = min(100, row_dt_percentile + 1) 
    
    for pctile in range(min_dt_percentile, max_dt_percentile + 1): 
        percentile_df = dt_percentiles_df_dict[pctile]
        all_nearby_count += percentile_df.query(all_nearby_query).shape[0]
        nearby_fires_count += percentile_df.query(nearby_fires_query).shape[0]

    all_nearby_count_label = 'all_nearby_count' + str(time_measure)	
    nearby_fires_count_label = 'all_nearby_fires' + str(time_measure)	
    output_dict = {'lat': lat, 'long': lng, 'date_fire': date, 
                    all_nearby_count_label: all_nearby_count, 
                    nearby_fires_count_label: nearby_fires_count}

    return output_dict

def _get_lat_long_range(lat, lng, dist_measure):
    """Calculate the min/max. lat/long to look for "nearby" obs in. 

    This is a helper function called from `query_for_nearby_fires`. 

    Args: 
    ----
        lat: float
            Latitude of the ob. to look around. 
        lng: float
            Longitude of the ob. to look around. 
        dist_measure: float 
            Holds how far to look around the ob.  

    Return: 
    ------
        lat_min: float
            Holds the minimum lat for an ob. to be considered "nearby". 
        lat_max: float  
            Holds the maximum lat for an ob. to be considered "nearby". 
        long_min: float  
            Holds the minimum long for an ob. to be considered "nearby". 
        long_max: float 
            Holds the maximum long for an ob. to be considered "nearby". 
    """

    lat_min, lat_max = lat - dist_measure, lat + dist_measure
    long_min, long_max = lng - dist_measure, lng + dist_measure

    return lat_min, lat_max, long_min, long_max

def _get_date_range(time_measure, dt):
    """Calculate the datetime range to look for "nearby" obs in. 
    
    This is a helper function called from `query_for_nearby_fires`. 

    Args: 
    ----
        time_measure: int
            Holds how many days to go back in time to look for
            nearby_fires. 
        dt: datetime.datetime
            Holds the date of the current ob. 

    Return: 
    ------ 
        date_min: datetime.datetime
            Holds the minimum date for an ob. to be considered "nearby". 
        date_max: Holds the maximum date for an ob. to be considered "nearby". 
    """

    if time_measure == 0: 
        hour, minute, second = dt.hour, dt.minute, dt.second
        date_min = dt - timedelta(hours=hour)
        date_min = date_min - timedelta(minutes=minute)
        date_min = date_min - timedelta(seconds = second)
    else: 
        date_min  = dt - timedelta(days=time_measure)
    
    date_max = datetime(dt.year, dt.month, dt.day, 0, 0, 0)

    return date_min, date_max

def _merge_results(df, nearby_count_dicts): 
    """Merge the inputted dictionary of data onto the DataFrame. 

    Take in the nearby_count_dict, and merge it into the current df. Merge 
    by lat, long, and date. The nearby_count_dict holds the information 
    calcalated in the query_for_nearby_fires function for each latitude, 
    longitude, and date combo. 

    This is a helper function called from `gen_nearby_fires_count`. 

    Args: 
    ----
        df: Pandas DataFrame
        nearby_count_dicts: list of dcts
    
    Return: 
    ------
        df: Pandas DataFrame
    """

    nearby_fires_df = pd.DataFrame(nearby_count_dicts)
    nearby_fires_df = nearby_fires_df.drop_duplicates()
    df = pd.merge(df, nearby_fires_df, how='inner', on=['lat', 'long', 'date_fire'])

    return df

