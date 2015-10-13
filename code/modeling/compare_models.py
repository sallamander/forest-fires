import pandas as pd
from sklearn.metrics import roc_auc_score
import sys

def output_csv_to_merge(model_name, suffix, all_cols=False): 
    '''
    Input: String, Boolean
    Output: Pandas DataFrame, Numpy Array 

    Take in the model name, and from that, read in a .csv into a pandas 
    dataframe. If all_cols is equal to true, then output all columns, plus one
    that holds the absolute difference between the fire boolean and the predicted
    probabilities from that model. Otherwise, output only the predicted 
    probabilities column from that model df. 
    '''
    filepath = '../model_output/days_forward_60/' + model_name + '_preds_probs_' + suffix + '.csv'
    df = pd.read_csv(filepath) 
    
    fire_bool = df.fire_bool 

    if all_cols == False: 
        keep_columns = [model_name] 
        df = df[keep_columns]
    else: 
        df['abs_diff'] = df.eval('fire_bool - ' + model_name)
        df['abs_diff'] = df['abs_diff'].abs()

    
    return df, fire_bool

def combine_dfs(input_df_list): 
    '''
    Input: List of Pandas DataFrames, String
    Output: Pandas DataFrame

    For the inputted Dataframes, merge them all together. 
    '''
    
    output_df = input_df_list[0]
    if len(input_df_list) > 1: 
        for df in input_df_list[1:]:
            output_df = output_df.merge(df, left_index=True, right_index=True) 
    return output_df 

def average_model_preds(combined_df): 
    '''
    Input: Pandas DataFrame 
    Output: Pandas DataFrame 

    The inputted dataframe will have columns, where each column is predicted probabilities 
    from a model. This function will average the predicted probabilities accross all columns. 
    ''' 
    
    cols = combined_df.columns
    num_cols = len(cols) 
    
    combined_df['average_col'] = 0
    for col in cols: 
        combined_df['average_col'] += combined_df[col]

    combined_df['average_col'] /= num_cols

    return combined_df 

def grab_top_n(df, top_n): 
    '''
    Input: Pandas DataFrame, Integer
    Output: Pandas DataFrame

    For the pandas dataframe, grab the rows with the top n values for the 
    absolute difference (between the fire_bool and the predicted probability).
    Here we are just looking to examine the observations that are the farthest
    off. 
    '''

    df.sort('abs_diff', inplace=True, ascending = False)
    return df.iloc[0:top_n, :]

if __name__ == '__main__': 
    if len(sys.argv) > 1: 
        all_cols = sys.argv[1]
    else: 
        all_cols = False

    model_list = {'logit': 'allprior_60', 
                  }
    
    input_df_list = []
    for k, v in model_list.iteritems(): 
        input_df, fire_bool = output_csv_to_merge(model_name = k, suffix = v, all_cols=all_cols)
        if all_cols == True: 
            input_df = grab_top_n(input_df, 50)
        input_df_list.append(input_df)

    combined_df = combine_dfs(input_df_list) 
    averaged_df = average_model_preds(combined_df)
    roc_auc = roc_auc_score(fire_bool, averaged_df['average_col'])

