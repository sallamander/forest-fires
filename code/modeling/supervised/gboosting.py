"""A module for gradient boosted models or helper functions/objects. 

Currently, this module just holds a callback class to implement
when using sklearn's GradientBoostingClassifier. 
"""

from sklearn.ensemble._gradient_boosting import predict_stage

class Monitor(object): 
    """Performs early stopping in an sklearn GradientBoostingClassifier. 

    This monitor checks the validation loss between each training stages, 
    stopping training when the validation loss has not decreased for 
    some inputted number of consecutive stages. 

    This code was taken and modified from: 

    https://henri.io/posts/using-gradient-boosting-with-early-stopping.html

    Everything is pretty much the exact same, except for docstrings, 
    variable names, and any updates necessary for API changes.  

    Args: 
    ----
        X_test: np.ndarray
        y_test: np.ndarray 
        tolerance: int
            Number of consecutive stages to allow the validation loss
            to increase before stopping training. 
    """

    def __init__(self, X_test, y_test, tolerance=5): 
        self.X_test = X_test
        self.y_test = y_test
        self.tolerance = tolerance 
        self.losses = []

    def __call__(self, idx, model, args): 
        """Used to determine if training should continue or stop. 

        When an object of this class is passed as the `monitor` argument
        to the `fit` method of a GradientBoostingClassifier, this method 
        is called after every training stage. It is automatically passed
        the arguments above, which can be used to evaluate the validation
        loss and determine whether to continue training. 

        This method draws heavily from functions/methods available on 
        a GradientBoostingClassifier that are less than obvious from the 
        sklearn docs - `_init_decision_function` and `predict_stage`. They 
        can be found in the source code in `_gradient_boosting.pyx`
        and `gradient_boosting.py` at the following: 

        https://github.com/scikit-learn/scikit-learn/tree/master/sklearn/ensemble

        Args: 
        ----
            idx: int
                Holds the current iteration. 
            model: sklearn.ensemble.GradientBoostingClassifier
                Instance of the GradientBoostingClassifier that is being 
                trained. 
            args: variable
                Holds, as the documentation puts it, "the local variables 
                of _fit_stages as keyword arguments". These aren't currently
                used in this method. 

        Return: 
        ------
            bool
                Returns True if training should stop, otherwise False. 
        """

        if not idx: 
            self.consecutive_decreases = 0
            self.predictions = model._init_decision_function(self.X_test)
        
        # By passing self.predictions as the last argument, we get the 
        # actual predictions assigned to it. 
        predict_stage(model.estimators_, idx, self.X_test, 
                model.learning_rate, self.predictions)
        self.losses.append(model.loss_(self.y_test, self.predictions))

        # If the loss gets worse, or if it only increases by < 0.005, 
        # count that as a consecutive decrease (e.g. one step closer to 
        # stopping early). 
        if len(self.losses) >= 2 and \
                (self.losses[-1] >= self.losses[-2] or \
                        abs(self.losses[-1] - self.losses[-2]) < 0.005): 
            self.consecutive_decreases += 1
        else:
            self.consecutive_decreases = 0

        if self.consecutive_decreases >= self.tolerance:
            print("Too many consecutive decreases of loss on validation set"
                  "({}): stopping early at iteration {}.".format(
                      self.consecutive_decreases, idx))
            return True
        else:
            return False
