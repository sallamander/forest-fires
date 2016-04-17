"""A module for instantiating supervised models for learning. 

This module exists to help separate out the pieces of the 
modeling process that occur in the `run_model.py` file. Its
sole focus is on supervised models, and it runs the gammit 
of them. For any model that isn't simply instantiated with 
only it's constructor (e.g. it requires an additional function, 
object, etc. to be built up), it is stored in another module
and imported. 
"""

import multiprocessing
import os
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier  
from xgboost.sklearn import XGBClassifier
from keras_net import KerasNet

def get_model(model_name, kwargs): 
    """Return an instance of the supervised model to be learned. 

    Args: 
    ----
        model_name: str
            Used to determine the model to instantiate. The use 
            of a string allows it to be passed from a command line
            argument (e.g. from `run_model.py`).  
        kwargs (optional): dct
            A dictionary of optional keyword arguments. The only one 
            that will be potentially used within this function is a
            `rand_seed` keyword argument, which will allow for the passing
            of a number to use as the `random_seed` on the models. 
            Otherwise, the expected arguments will be passed through to other
            functions to dictate how to construct the models. 

    Return: 
    ------
        model: instantiated model (varying)
    """

    # If the user isn't "sallamander", I'm assuming it's being run on 
    # a dedicated instance, so we'll want to use all available cores. 
    n_usable_cores = multiprocessing.cpu_count() \
        if os.environ['USER'] != 'sallamander' else 2

    rand_seed = kwargs.get('rand_seed', 24)

    if model_name == 'logit': 
        model = LogisticRegression(random_state=rand_seed)
    elif model_name == 'random_forest': 
        model = RandomForestClassifier(random_state=rand_seed, 
                 n_jobs=n_usable_cores)
    elif model_name == 'extra_trees': 
        model = ExtraTreesClassifier(random_state=rand_seed)
    elif model_name == 'gboosting': 
        model = GradientBoostingClassifier(random_state=rand_seed)
    elif model_name == 'neural_net': 
        model = KerasNet(kwargs)
    elif model_name == 'xgboost': 
        model = XGBClassifier(seed=rand_seed)
    else: 
        raise Exception("Invalid model name! Try again...") 

    return model 
