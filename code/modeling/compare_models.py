import pandas as pd
from sklearn.metrics import roc_auc_score

def output_csv_to_merge(model_name): 
    '''
    Input: String
    Output: Pandas DataFrame 
    '''
    filepath = '../model_output/' + model_name + '_preds_probs.csv'
    df = pd.read_csv(filepath) 
    
    fire_bool = df.fire_bool
    keep_columns = [model_name]
    df = df[keep_columns]
    
    return df, fire_bool

def combine_dfs(input_df_list): 
    '''
    Input: List of Pandas DataFrames 
    Output: Pandas DataFrame
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

if __name__ == '__main__': 
    model_csv_list = ['random_forest', 'gradient_boosting', 'logit']
    
    input_df_list = []
    for model_name in model_csv_list:
        input_df, fire_bool = output_csv_to_merge(model_name)
        input_df_list.append(input_df)
    
    combined_df = combine_dfs(input_df_list) 
    averaged_df = average_model_preds(combined_df)
    roc_auc = roc_auc_score(fire_bool, averaged_df['average_col'])

