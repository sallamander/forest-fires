import numpy as np
from sklearn.metrics import auc, precision_recall_curve, make_scorer

def return_scorer(name): 
    """Return an eval_metric based off of an inputted string. 

    For now this simply builds a metric that gives the AUC of the
    precision recall curve. 

    Args: 
    ----
        name: str

    Return: 
    ------
        callable_metric: sklearn.metric object
    """

    if name == 'auc_precision_recall': 
        callable_metric = make_scorer(auc(precision_recall_curve))

    return callable_metric

def return_score(y_true, y_pred_probs, name='auc_precision_recall'): 
    """Return the score from the inputted ground truth and predicted probabilities. 

    Args: 
    ----
        y_true: np.ndarray
        y_pred_probs: np.ndarray
        name: str
            Holds the name used to determine what score to use. 

    Return: 
    ------
        score: float 
    """

    scorer = return_scorer(name)
    score = scorer(y_true, y_pred_probs)
    return score

