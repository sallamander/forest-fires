"""A module for working with the results from modeling"""

import os
import sys
import pandas as pd

def gen_weights(metrics_df): 
    """Generate columns holding possible weights to use on the metrics. 

    Possible weighting schemes to use to weight the metrics across the 
    365 days of testing are: 

    (1) The fraction of total yearly observations that occur on that given day.
    (2) The fraction of total yearly `True` observations that occur on that 
        day (e.g. the fraction of total yearly forest-fires). 

    Args:
    ----
        metrics_df: Pandas DataFrame
    
    Returns:
    -------
        metrics_df: Pandas Dataframe
    """

    total_obs = metrics_df['num_obs'].sum()
    total_fires = metrics_df['num_fires'].sum()

    metrics_df.eval('total_weighting = num_obs / @total_obs')
    metrics_df.eval('fire_weighting = num_fires / @total_fires')

    return metrics_df

def gen_weighted_metrics(metrics_df): 
    """Generate columns holding the weighted value of a metric.

    Args:
    ----
        metrics_df: Pandas DataFrame

    Returns: 
    -------
        metrics_df: Pandas DataFrame
    """

    metrics_df.eval('tweighted_roc_auc = total_weighting * roc_auc')
    metrics_df.eval('tweighted_pr_auc = total_weighting * pr_auc')
    metrics_df.eval('fweighted_roc_auc = fire_weighting * roc_auc')
    metrics_df.eval('fweighted_pr_auc = fire_weighting * pr_auc')

    return metrics_df

def read_df(feats_dir_path, filepath):
    """Read in the .csv at the given filepath

    Args: 
    ----
        filepath: str

    Returns: 
    -------
        df: Pandas DataFrame
    """

    dt = filepath.split('_')[1][:-4]
    df = pd.read_csv(feats_dir_path + filepath)
    df.drop('num_obs', inplace=True, axis=1)
    df.set_index('feat_names', inplace=True)
    df.rename(columns={'importance':dt}, inplace=True)

    return df

if __name__ == '__main__':
    df_path = sys.argv[1]
    feats_dir_path = sys.argv[2]

    metrics_df = pd.read_csv(df_path, header=None, names=['dt', 'num_obs', 
        'num_fires', 'roc_auc', 'pr_auc'], na_values=['None'])
    metrics_df.dropna(inplace=True)
    metrics_df = gen_weights(metrics_df)
    metrics_df = gen_weighted_metrics(metrics_df)

    print 'Total Weighted ROC AUC: {}'.format(metrics_df.tweighted_roc_auc.sum())
    print 'Total Weighted PR AUC: {}'.format(metrics_df.tweighted_pr_auc.sum())
    print 'Fire Weighted ROC AUC: {}'.format(metrics_df.fweighted_roc_auc.sum())
    print 'Fire Weighted PR AUC: {}'.format(metrics_df.fweighted_pr_auc.sum())

    final_df = pd.concat((read_df(feats_dir_path, filepath) for filepath 
            in os.listdir(feats_dir_path)), axis=1)

