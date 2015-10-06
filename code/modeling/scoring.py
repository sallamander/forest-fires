from sklearn.metrics import accuracy_score, precision_score, roc_auc_score, recall_score

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
			score_dictionary[score_metric.func_name] = score_metric(y_true, y_pred)

	return score_dictionary
