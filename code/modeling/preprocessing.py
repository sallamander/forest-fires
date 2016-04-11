"""A module for preprocessing a DataFrame before modeling. 

This is a module containing functions for preprocessing 
the data before inputting it into models, but after any/all
feature engineering is complete. 
"""

from datetime import datetime, timedelta

def normalize_df(input_df): 
    """Perform a normalization on all numerical columns that aren't Y.

    Specfically, perform a normalization on each column by subtracting
    off its mean and dividing by its standard deviation. 

    Args: 
    ----
        input_df: Pandas DataFrame
            Holds the unnormalized data. 

    Return: 
    ------
        output_df: Pandas DataFrame
            Holds the normalized data. 
    """
        

    output_df = input_df.copy()
    for col in input_df.columns: 
        if col not in ('fire_bool', 'date_fire'): 
            output_df[col] = (input_df[col] - input_df[col].mean()) \
                / input_df[col].std()

    return output_df 

def prep_data(input_df): 
    """Fill in N/A's and inf. values, and drop the `date_fire` column. 

    Args: 
    ----
        input_df: Pandas DataFrame
    
    Return: 
    ------
        output_df: Pandas DataFrame 
    """

    output_df = df.fillna(-999)
    output_df.replace(np.inf, -999, inplace=True)
    output_df.drop('date_fire', inplace=True, axis=1)

    return output_df

def get_target_features(input_df): 
    """Separate out the target from the features and return both. 

    Target - `fire_bool`
    Features - Everything else 

    Args: 
    ---- 
        input_df: Pandas DataFrame

    Return: 
    ------
        target: Pandas DataFrame 
            Holds the `fire_bool` column only. 
        features: Pandas DataFrame 
            Holds all columns from the original `input_df`, except
            the `fire_bool` column. 
    """

    target = df.fire_bool
    features = df.drop('fire_bool', axis=1)
    
    return target, features

def alter_nearby_fires_cols(input_df): 
    """Correct for incorrect values in input_df. 

    When constructing the columns for `all_nearby_count365`, 
    `all_nearby_fires365`, and their equivalents for 2 and 3 years, 
    the fact that some obs. in the dataset did not have that many 
    years of data prior to them was not accounted for. 
    
    These columns hold the number of nearby obs. or fires that were 
    around the ob. in space and time, where the # in the column name 
    gives the time in terms of days. Thus, 365 refers to any obs. 
    around them in space, up to 365 days prior. For all of the observations
    in 2012, this isn't actually possible (since it's the first year). 
    Similarly, this isn't possible for the 730 days column for any
    observations in 2012 or 2013, or for the 1095 column for any obs. 
    in 2012-2014. This function will correct that by filling in `Nans` for 
    these values (although those `Nans` will be filled in later when the 
    `prep_data` function from above is called on the DataFrame. 

    Args: 
    ----
        input_df: pandas DataFrame 

    Return: 
    ------
        output_df: pandas DataFrame
    """

    start_date = datetime(2013, 1, 1, 0, 0, 0)

    # Go forward the key number of days (0, 365, or 730), and replace
    # all the columns in the value list with 'Nans'. I could have compacted
    # the lists here, but it probably would have been at the cost of a 
    # little bit of clarity and readability. 
    replace_dct = {0: ['all_nearby_count365', 'all_nearby_fires365'], 
                   365: ['all_nearby_count365', 'all_nearby_fires365', 
                        'all_nearby_count730', 'all_nearby_fires730']
                   730: ['all_nearby_count365', 'all_nearby_fires365', 
                        'all_nearby_count730', 'all_nearby_fires730', 
                        'all_nearby_count1095', 'all_nearby_fires1095']}

    output_df = input_df.copy()
    for days_forward, col_names in replace_dct.iteritems(): 
        break_date = start_date + timedelta(days=days_forward)
        for col_name in col_names: 
            output_df.loc[df['date_fire'] < break_date, col_name] \
                    = np.float('inf')

    return output_df 

