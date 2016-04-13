"""A module for score metrics used during model training/evaluation. 

This module provides a function for returning an individual scorer 
function that can be used to train/evaluate models, as well as
a function that returns a score for inputted predictions. Finally, 
it offers a class for calculating the area under a precision recall
curve.
"""
import numpy as np
from sklearn.metrics import auc, precision_recall_curve, make_scorer

def return_scorer(name='auc_precision_recall'): 
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
        precision_recall_auc = PrecisionRecallAUC()
        callable_metric = precision_recall_auc 

    return callable_metric

class PrecisionRecallAUC(object): 
    """A class for allowing precision recall AUC as a scorer metric. 

    This class acts as a callable that can calculate the area 
    under the precision recall curve, or be passed as a scoring metric
    to the `sklearn.GridSearchCV` class when performing cross-validation. 
    """

    def __call__(self, estimator, X_test, y_test): 
        """Predict on X_test with the estimator, and evaluate using y_test.  
        
        Predict on `X_test` using the inputted estimator. Take the resulting
        predictions, and calculate the area under the precision recall curve
        for those predictions and `y_test`. 

        Args: 
        ----
            estimator: varied 
                Must implement a `fit` method that takes in an input 
                matrix and outputs predictions. 
            X_test: np.ndarray
            y_test: np.ndarray

        Return: 
        ------
            pr_auc: float
                Holds the area under the precision recall curve for `y_test`
                compared to the predictions from the estimator on `X_test`. 
        """
                
        y_preds = estimator.predict_proba(X_test)[:, 0]
        prec, rec, thresholds = precision_recall_curve(y_test, y_preds)

        pr_auc = auc(rec, prec)
        
        return pr_auc

