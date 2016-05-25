"""A module for logging different results during training and testing."""

from datetime import datetime
import time
import numpy as np
import pandas as pd

def log_train_results(model_name, train, best_fit_model, best_score, 
                      score_type): 
    """Log the results of our best model run. 

    Args: 
    ----
        model_name: str
        train: np.ndarray
            Used to store the column names. 
        best_fit_model: variable 
            Used to store the final parameters of the best model. 
        best_score: float 
            Best score from the fitted model. 
        score_type: str
    """

    st = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    filename = 'code/modeling/model_output/logs/{}.txt'.format(model_name)
    with open(filename, 'a+') as f:
        f.write(st + '\n')
        f.write('-' * 100 + '\n')
        f.write('Model Run: {}\n\n'.format(model_name))
        f.write('Params: {}\n\n'.format(best_fit_model.get_params())) 
        f.write('Features: {}\n\n'.format(', '.join(train.columns)))
        f.write('Train {}: {}\n\n'.format(score_type, best_score))

def log_test_results(dt, y_true, preds_probs, roc_auc, pr_auc): 
    """Log all of the passed in results.  
    
    Store the predicted probabilities as a '.csv', and log the ROC_AUC
    and PR_AUC in A CSV file with a date column and two columns for 
    the metrics. 

    Args: 
    ----
        dt: datetime.datetime
        y_true: 1d np.ndarray
        preds_probs: 1d np.ndarray
        roc_auc: float
        pr_auc: float
    """
   
    save_dt = '-'.join([str(dt.year), str(dt.month), str(dt.day)])
    base_fp = 'code/modeling/model_output/'
    preds_probs_fp = base_fp + 'pred_probs/preds_probs_{}.csv'.format(save_dt)
    np.savetxt(preds_probs_fp, preds_probs, delimiter=',')
   
    num_obs = y_true.shape[0]
    num_fires = y_true.sum()

    metrics_fp = base_fp + 'metrics.csv'
    with open(metrics_fp, 'a+') as f: 
        out_str = ','.join([str(save_dt), str(num_obs), str(num_fires), 
            str(roc_auc), str(pr_auc)]) + '\n'
        f.write(out_str)

def log_feat_importances(model, X_train, dt): 
    """Log the feature importances for a model fit on a given date. 

    Args: 
    ----
        model: varied tree-based model
            Fit tree-based model that has a `feature_importances_` attribute`.
        X_train: 2d np.ndarray
            Used to obtain the names of the columns corresponding to the features. 
        dt: datetime.datetime
    """

    save_dt = '-'.join([str(dt.year), str(dt.month), str(dt.day)])
    feat_importances = model.feature_importances_
    feats_sorted = np.argsort(feat_importances)

    feat_names = X_train.columns[feats_sorted]
    feats_vals_ordered = feat_importances[feats_sorted]
    feats_vals_ordered = feats_vals_ordered / feats_vals_ordered.max() * 100

    feats_df = pd.DataFrame()
    feats_df['feat_names'] = feat_names
    feats_df['importance'] = feats_vals_ordered
    feats_df['num_obs'] = X_train.shape[0]

    save_fp = 'code/modeling/model_output/feat_importances/feats_' + \
            save_dt + '.csv'

    feats_df.to_csv(save_fp, index=False)
