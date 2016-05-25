"""A module supporting time-fold validation with generators. 

This module provides a couple of classes that can be used as generators to 
perform time-fold validation. The motivation behind these classes was the 
lack of easy (or really any) to use generators that could be passed into 
GridSearchCV in sklearn.grid_search in the case of working with time-series
data (at the time of writing - it's apparently currently in the works with 
sklearn). 
"""

import numpy as np
import pandas as pd
from datetime import timedelta, datetime

class SequentialTimeFold():
    """Sequential time fold cross-validation iterator. 

    Provides train/test indices to split the data based off a date or datetime 
    column. The user primarily inputs a dataframe holding a date column, 
    and a step size by which to generate the folds. Folds are then created in a 
    sequential manner, where all obs. on days before the (test_date - step_size) 
    are in the training set, and all obs. on the test_date are in the test set. 

    Args: 
    ----
        df: pandas DataFrame
            Holds the data to iterate over and build the generator out of. 
        step_size: datetime.timedelta
            Holds the number of days to move backward during each `next()` call 
            on the generator. If `step_size` is 10 days, then we perform a 
            train/test split based off some date, and then move backward in time 
            by 10 days, and use that as the new date to perform the next train/test 
            split. This will typically be one (e.g. we'll perform the train/test 
            split, move back a day, and then perform the next one). 
        max_folds: int
            Holds the max number of folds (or `next` calls) to allow. 
        test_set_date: datetime.datetime
            Holds the beginning day (plus days_forward) to split on. 
        y_col: str
            Used to determine if there is only one class in the outputted
            train or test sets. 
        days_forward (optional): int
            Basically holds the number of days that will be included as part of
            the test set. If 30, then the test set will include 30 days, and these
            will be the 30 days later in time past the current self.test_date. This
            number will typically correspond to `step_size`. 

    Example: 
    -------
        `step_size`: 10 days
        `test_set_date`: January 1st, 2014
        `days_forward`: 10 days

        Since the passed in `test_set_date` is actually the first day + 
        `days_forward` to split on, the first date actually split on for train/test
        is actually `days_forward` before that, or here December 22nd, 2013. 
        From there, we move backwards in time by `step_size` and consider each 
        step back a new date to split on. When we split, all obs. before the date
        that is split on are in the train, and all after are in the test. We 
        iterate and take steps backwards (by the `step_size`) until we hit 
        the number of `max_folds`. In the end, our folds here would end up with 
        the following dates: 

        Fold 1: December 22nd, 2013 - January 1st, 2014
        Fold 2: December 12th, 2013 - December 22, 2013
        Fold 3: December 2nd, 2013 - December 12th, 2013
        Fold 4: November 22nd, 2013 - December 2nd, 2013
        Fold 5: November 12th, 2013 - November 22nd, 2013
        Fold 6: November 2nd, 2013 - November 12th, 2013
        Fold 7: October 23rd, 2013 - November 2nd, 2013
        Fold 8: October 13th, 2013 - October 23rd, 2013 
        Fold 9: October 3rd, 2013 - October 13th, 2013
        Fold 10: September 23rd, 2013 - October 3rd, 2013 
    """

    def __init__(self, df, step_size, max_folds, test_set_date, y_col,         
                 days_forward=None): 

        self.df = df
        self.step_size = step_size
        self.days_forward = self.step_size if not days_forward else days_forward
        self.max_folds = max_folds
        self.y_col = y_col

        self.n_folds = 0
        self.all_dates = df['date_fire'] 
        # Set the first test_date to be the most recent set of day(s). 
        self.test_date = test_set_date - timedelta(days=days_forward)
        
    def __len__(self): 
        return self.n_folds

    def __iter__(self): 
        """Allows the class to be called as an iterator."""
        return self

    def next(self):
        """Generate integer indices corresponding to train/test sets. 
        
        At the first iteration, take all those observations that are on 
        `self.test_date` as the test set, and all observations prior to that in 
        time as the training set. Generate subsequent train/test splits (folds) 
        by stepping back through time by `self.step_size` and performing new splits. 

        Return: 
        ------
            train_indices: np.ndarray
            test_indices: np.ndarray
        """
        
        # Initialize array to initially get into while loop. 
        test_indices = np.zeros((0))

        while test_indices.shape[0] == 0: 
            # Define a min and max for the test set to query against. 
            test_date_min = self.test_date
            test_date_max = test_date_min + timedelta(days=self.days_forward)

            test_indices = np.where(np.logical_and(self.all_dates >= test_date_min, 
                self.all_dates < test_date_max))[0]
            train_indices = np.where(self.all_dates < test_date_min)[0]
            self.test_date -= self.step_size
            
            # If it's all one label in the test indices, then we can't calculate the 
            # metrics I'm looking at, and should just resample.
            if len(np.unique(self.df.ix[test_indices, self.y_col])) != 2: 
                test_indices = np.zeros((0))
        
        if self.n_folds <= self.max_folds: 
            self.n_folds += 1
            return train_indices, test_indices
        else: 
            raise StopIteration()

