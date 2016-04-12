import numpy as np
from sklearn.metrics import auc, precision_recall_curve, make_scorer, 
    accuracy_score, precision_score, roc_auc_score

def return_eval_metric(name): 
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

def return_scores(y_true, y_pred, y_pred_probs): 
	'''
	Input: Numpy Array, Numpy Array
	Output: Float, Float, Float, Float

	For the given set of true and predicted y_values (i.e. if it's a forest fire or not), 
	return the accuracy_score, precision_score, roc_auc_score, and recall_score. 
	'''
	score_metrics = [accuracy_score, precision_score, roc_auc_score, recall_score]
	score_dictionary = {}

	for score_metric in score_metrics: 
		if score_metric.func_name == 'roc_auc_score': 
			score_dictionary[score_metric.func_name] = score_metric(y_true, y_pred_probs[:, 1])
		else: 
			scores = np.array([score_metric(y_true, return_y_preds(y_pred_probs, threshold)) for threshold in xrange(0, 101)])
			score_dictionary[score_metric.func_name] = scores.max()

	return score_dictionary

def return_y_preds(y_pred_probs, threshold): 
	'''
	Input: Numpy Array, Integer
	Output: Numpy Array

	For the inputted array of predicted probabilities, return a numpy array that is 1's or 0's, 
	where 1's are those predicted probabilities that are above the threshold.
	'''

	return y_pred_probs[:, 1] > (threshold / 100.0)
