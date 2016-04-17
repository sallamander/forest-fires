"""A module for creating Keras neural net models. 

This module holds a class for easier generation of Keras 
neural network models, meant to allow for fast iteration
and prototyping. For the time being, it works for 
vanilla, fully-connected feed-forward networks. Hopefully 
it'll be built out in the future. 
"""

import numpy as np
from keras.models import Sequential 
from keras.layers.core import Dense, Dropout
from keras.optimizers import RMSprop
from keras.callbacks import EarlyStopping

class KerasNet(object): 
    """A wrapper around a neural network built with Keras. 

    This class is meant to abstract away the building of a 
    Keras network and add some ease of interaction in terms of 
    building a network. For example, layers are simply passed in 
    by adding a dictionary into the `**kwargs` argument passed to
    the `__init__` method: 

    {'layer_10': {'num': 10, 'nodes': 64, 'activation': 'relu', 
        'weight_init': 'glorot_uniform', 'dropout': 0.35}}

    In this manner, it should be fairly easy to add additional layers, 
    as well as adjust/tune current layers. This may/may not be 
    extendable/scalable, but for now this is meant to be used for 
    fairly vanilla flavored nets and allow for ease of tuning. 

    Args: 
    ----
        **kwargs: dct 
            Holds the instructions on how to build the Keras model. 
            It is expected that a `num_layers` argument will be passed
            in, and that there will be a `layer_#` for every layer 
            up to the `num_layers` passed in. For the time being, 
            the arguments passed with `layer_#` allow for anything
            passed to `Dense` or `Dropout` layers in Keras. 

            http://keras.io/layers/core/#dense
            http://keras.io/layers/core/#dropout
    """

    def __init__(self, kwargs): 
        
        self.num_layers = kwargs.pop('num_layers', None) 
        assert self.num_layers, "Need a 'num_layers' argument passed in."
        self.rand_seed = kwargs.pop('rand_seed', 24)
        
        assert_str = """Number of layers doesn't align with the numbers of the 
            other arguments (activations, weight inits, ect.).""".replace('\n', '')
        self.layers = []
        for num_layer in xrange(1, self.num_layers + 1): 
            layer = kwargs.pop('layer_' + str(num_layer), None)
            assert layer, assert_str
            self.layers.append(layer)
        
        self.model = self._build_net()
    
    def _build_net(self): 
        """Build the Keras network according to the specifications.

        Construct the model, but don't compile it. 

        Return: keras.models.Sequential
        """

        np.random.seed(self.rand_seed)

        model = Sequential()

        for layer in self.layers:
            model = self._add_layer(model, layer)

        return model 

    def _add_layer(self, model, layer): 
        """Add a layer to the Keras model according to the specifications.
        
        Args: 
        ----
            model: keras.models.Sequential 
            layer: dct
                Holds keyword arguments to specify how to add the layer. 

        Return: 
        ------
            model: keras.models.Sequential
        """
        
        # We need these arguments to continue. 
        num_layer = layer.pop('num', None) 
        num_nodes = layer.pop('nodes', None)
        assert num_layer, "Need to know the number of each layer."
        assert num_nodes, "Need to know the number of nodes in each layer."

        if num_layer == 1: 
            input_dim = layer.pop('input_dim', None)
            assert input_dim, "Need an input dimension for the first layer."

        # Use Keras defaults if nothing passed in. 
        weight_init = layer.pop('weight_init', 'glorot_uniform')
        activation = layer.pop('activation', 'linear')
        
        dropout = layer.pop('dropout', None)
        
        # Use keyword arguments to avoid any ambiguity. 
        model.add(Dense(output_dim=num_nodes, init=weight_init, 
            activation=activation, input_dim=input_dim))

        if dropout: 
            model.add(Dropout(p=Dropout))

        return model 
        
    def fit(self, X_train, y_train, **kwargs): 
        """Compile and fit the model. 

        Args: 
        ----
            X_train: np.ndarray
            y_train: np.ndarray
            **kwargs: dct
                Optional arguments to pass to the `compile` and 
                `fit` steps of the model. Potential (and somewhat
                expected) arguments are the following: 

                loss: str
                optimizer: str
                X_test: np.ndarray
                y_test: np.ndarray
                nb_epoch: int
                batch_size: int
                early_stopping: int
                    Holds the "patience" to pass on to the EarlyStopping
                    object from Keras.callbacks. 
        """

        loss = kwargs.pop('loss', 'categorical_crossentropy')
        optimizer = kwargs.pop('optimizer', 'rmsprop')
        early_stopping = kwargs.pop('early_stopping', False)

        self.model.compile(loss=loss, optimizer=optimizer)

        nb_epoch = kwargs.pop('nb_epoch', 2)
        batch_size = kwargs.pop('batch_size', 32)
        X_test = kwargs.pop('X_test', None)
        y_test = kwargs.pop('y_test', None)

        if X_test is not None and y_test is not None:
            validation_data = (X_test, y_test)

        if early_stopping: 
            early_stopper = EarlyStopping(monitor='val_loss', 
                    patience=early_stopping, verbose=1)
        self.model.fit(X_train, y_train, batch_size=batch_size, nb_epoch=nb_epoch, 
                verbose=1)
        

