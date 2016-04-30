"""A module for working with the results from modeling"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def gen_weights(metrics_df, by_month=False): 
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

    if not by_month: 
        total_obs = metrics_df['num_obs'].sum()
        total_fires = metrics_df['num_fires'].sum()

        metrics_df.eval('total_weighting = num_obs / @total_obs')
        metrics_df.eval('fire_weighting = num_fires / @total_fires')
    else: 
        metrics_df['month'] = metrics_df['dt'].apply(lambda row: 
                row.split('-')[1]).astype(int)
        months_groupby = metrics_df.groupby('month')
        obs_per_month = months_groupby['num_obs'].sum()
        obs_per_month.name = 'total_obs'
        fires_per_month = months_groupby['num_fires'].sum()
        fires_per_month.name = 'total_fires'
        metrics_df = metrics_df.join(obs_per_month, on='month')
        metrics_df = metrics_df.join(fires_per_month, on='month')

        metrics_df.eval('total_weighting = num_obs / total_obs')
        metrics_df.eval('fire_weighting = num_fires / total_fires')

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
    metrics_df = gen_weights(metrics_df, by_month=True)
    metrics_df = gen_weighted_metrics(metrics_df)

    '''
    print 'Total Weighted ROC AUC: {}'.format(metrics_df.tweighted_roc_auc.sum())
    print 'Total Weighted PR AUC: {}'.format(metrics_df.tweighted_pr_auc.sum())
    print 'Fire Weighted ROC AUC: {}'.format(metrics_df.fweighted_roc_auc.sum())
    print 'Fire Weighted PR AUC: {}'.format(metrics_df.fweighted_pr_auc.sum())
    '''

    for month in range(3, 13): 
        print month
        print '-' * 50
        metrics_df2 = metrics_df.query('month == @month')
        print 'Total Weighted ROC AUC: {}'.format(metrics_df2.tweighted_roc_auc.sum())
        print 'Total Weighted PR AUC: {}'.format(metrics_df2.tweighted_pr_auc.sum())
        # print 'Fire Weighted ROC AUC: {}'.format(metrics_df2.fweighted_roc_auc.sum())
        # print 'Fire Weighted PR AUC: {}'.format(metrics_df2.fweighted_pr_auc.sum())

    final_df = pd.concat((read_df(feats_dir_path, filepath) for filepath 
            in os.listdir(feats_dir_path)), axis=1)

    top_10 = final_df.mean(axis=1).sort_values()[-10:]
    labels = ['Nearby Fires - 1095', 'Temperature', 'Fire Radiative Power', 
            'Nearby Obs. - 5', 'Hour of Day', 'Latitude', 'Nearby obs. - 4',
            'Longitude', 'Nearby Fires - 6', 'Nearby Fires - 4']
    top_10 = top_10.sort_values(ascending=True)
    plt.figure(figsize=(12, 5))
    ax = sns.barplot(x=top_10.values, y=labels, color='r')
    ax.grid(False)
    ax.set_xlabel("Feature Importances")
    plt.savefig('feat_importances.png')

