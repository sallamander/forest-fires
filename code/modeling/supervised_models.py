"""A module for instantiating supervised models for learning. 

This module exists to help separate out the pieces of the 
modeling process that occur in the `run_model.py` file. Its
sole focus is on supervised models, and it runs the gammit 
of them. 
"""

import multiprocessing
import os
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, 
    GradientBoostingClassifier 


def get_model(model_name, train_data, rand_seed=None): 
    """Return an instance of the supervised model to be learned. 

    Args: 
    ----
        model_name: str
            Used to determine the model to instantiate. The use 
            of a string allows it to be passed from a command line
            argument (e.g. from `run_model.py`).  
        train_data: Pandas DataFrame
            Used in the case that the size of the input data needs 
            to be known (e.g. fitting a Neural Network). 
        rand_seed (optional): int
            Number used to set the random seed. 

    Return: 
    ------
        model: instantiated model (varying)
    """

    # If the user isn't "sallamander", I'm assuming it's being run on 
    # a dedicated instance, so we'll want to use all available cores. 
    n_usable_cores = multiprocessing.cpu_count() \
        if os.environ['USER'] != 'sallamander' else 2

    if model_name == 'logit': 
         model = LogisticRegression(random_state=rand_seed)
    elif model_name == 'random_forest': 
         model = RandomForestClassifier(random_state=rand_seed, 
                 n_jobs=n_usable_cores)
    elif model_name == 'gradient_boosting': 
         model = GradientBoostingClassifier(random_state=rand_seed)
    elif model_name == 'neural_net': 
         model = get_neural_net(train_data)
    else: 
        raise Exception("Invalid model name! Try again...") 

