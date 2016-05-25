"""A module for instantiating supervised models for learning. 

This module exists to help separate out the pieces of the modeling process that 
occur in the `run_model.py` file. Its sole focus is on supervised models, and
it can be used to run the gammit of them.
"""

import multiprocessing
import os
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier  
from xgboost.sklearn import XGBClassifier

def get_model(model_name): 
    """Return an instance of the supervised model to be learned. 

    Args: 
    ----
        model_name: str
            Used to determine the model to instantiate. 

    Return: 
    ------
        model: instantiated model (varying)
    """

    # If the user isn't "sallamander", I'm assuming it's being run on 
    # a dedicated instance, so we'll want to use all available cores. 
    n_usable_cores = multiprocessing.cpu_count() \
        if os.environ['USER'] != 'sallamander' else 2

    rand_seed = 24 

    if model_name == 'logit': 
        model = LogisticRegression(random_state=rand_seed)
    elif model_name == 'random_forest': 
        model = RandomForestClassifier(random_state=rand_seed, 
                 n_jobs=n_usable_cores)
    elif model_name == 'extra_trees': 
        model = ExtraTreesClassifier(random_state=rand_seed, n_jobs=n_usable_cores)
    elif model_name == 'gboosting': 
        model = GradientBoostingClassifier(random_state=rand_seed)
    elif model_name == 'neural_net': 
        model = KerasNet(kwargs)
    elif model_name == 'xgboost': 
        model = XGBClassifier(seed=rand_seed)
    else: 
        raise Exception("Invalid model name! Try again...") 

    return model 
