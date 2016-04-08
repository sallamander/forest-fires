"""A module for preprocessing a DataFrame before modeling. 

This is a module containing functions for preprocessing 
the data before inputting it into models, but after any/all
feature engineering is complete. 
"""

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
