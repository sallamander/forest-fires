"""A module supporting time-fold validation with generators. 

This module provides a couple of classes that can be used as 
generators to perform time-fold validation. The motivation 
behind these classes was the lack of easy (or really any) 
to use generators that could be passed into GridSearchCV
in sklearn.grid_search in the case of working with time-series
data. 
"""

import numpy as np
import pandas as pd
from datetime import timedelta, datetime

class BaseTimeFold(object):
    """Base class for a cross-validation iterator.

    This class provides a base class to build other 
    time-series generator classes off of. It provides 
    four methods that classes built off of it inherit: 

    * __len__(): This is a method required by the GridSearchCV
      object from sklearn.GridSearchCV. 
    * _check_resample(): Helps to determine whether to re-sample
      the inputted data. 
    * _resample(): Performs re-sampling if it is desired. 
    * __iter__(): Allows an instance of the class to be used as an 
      iterator. 
    
    The classes that inherit then build up the methods that actual 
    implement the generator themselves. This generator will yield 
    pairs of (X_train_indices, X_test_indices), as the GridSearchCV
    `cv` argument expects. 

    Args: 
    ----
        df: pandas DataFrame
            Holds the data to iterate over and build the generator out 
            of. 
        step_size: datetime.timedelta
            Holds the number of days to move backward during each `next()`
            call on the generator. If `step_size` is 10 days, then we perform 
            a train/test split based off some date, and then move backward
            in time by 10 days, and use that as the new date to perform 
            the next train/test split. This will typically be one (e.g.
            we'll perform the train/test split, move back a day, and then 
            perform the next one). 
        max_folds: int
            Holds the max number of folds (or `next` calls) to allow. 
        test_set_date: datetime.datetime
            Holds the beginning day (plus 1) to split on. 
        y_col (optional): str
            Name of the target variable, used to determine if re-sampling
            is necessary. Required to be passed in if `resample_y_pct`
            and `resample_method` are passed in. 
        resample_y_pct (optional): float 
            Holds the minimum percentage of the True class to allow before
            performing re-sampling (e.g. if it goes lower, then perform 
            re-sampling via the `resample_method` specified). Required to 
            be passed in if `resample_method` is passed in. 
        resample_method (optional): str
            Holds the method to use for re-sampling ('upsample' or 'downsample').
            Required to be passed in if `resample_y_pct` is passed in. 
    """

    def __init__(self, df, step_size, max_folds, test_set_date, y_col=None, 
            resample_y_pct=None, resample_method=None):
        
        self.n_folds = 0
        self.max_folds = max_folds
        self.df = df
        self.all_dates = df['date_fire'] 
        self.step_size = step_size
        self.test_date = test_set_date - timedelta(days=1)
        
        if resample_y_pct and not (resample_method and y_col) or \
                resample_method and not (resample_y_pct and y_col):  
            raise Exception('Must pass in both resample_y_pct and resample_method, or neither at all.')

        self.y_col = y_col
        self.resample_method = resample_method
        self.resample_y_pct = resample_y_pct

    def __len__(self): 
        return self.n_folds

    def __iter__(self): 
        """Allows the class to be called as an iterator."""
        return self

    def _check_resample(self, train_indices): 
        """Check if resampling is necessary. 
        
        Check the precent of obs. that are `True` in `self.y_col`. If
        it is smaller than `self.resample_y_pct`, then perform re-sampling, 
        as noted by the `self.resample_method` attribute. 

        Args: 
        ----
            train_indices: np.ndarray
                Holds the training indices, used to check the percent of obs. 
                that are True and determine if re-sampling should be performed.

        Return: 
        ------
            train_indices: np.ndarray
                Holds the indices to use if re-sampling was performed, and 
                otherwise just the originally inputted indices. 
        """

        training_perc_y = self.df.ix[train_indices, self.y_col].mean()
        
        if training_perc_y > self.resample_y_pct: 
            return train_indices
        else: 
            train_indices = self._resample(train_indices)
            return train_indices

    def _resample(self, train_indices): 
        """Perform re-sampling via the specified method stored on `self`. 

        Conduct resampling as noted by the `self.resample_method` attribute. 
        "upsample" will just be duplicating a # of random positive 
        cases; "downsample"  will be taking all positive cases and an
        equal number of random negative cases. 

        Args: 
        ----
            train_indices: np.ndarray
                Holds the indices of obs. to re-sample from. 

        Return: 
        ------
            train_indices: np.ndarray
                Holds the indices of the original obs., plus any added
                during re-sampling. 
        """

        if self.resample_method == 'upsample': 
            true_indices = np.where(self.df[y_col] == True)[0]
            positive_indices = np.intersect1d(true_indices, train_indices)

            # Get a random sample from the positive indices, equal in size. 
            resampled_indices = np.random.choice(positive_indices, 
                    positive_indices.shape[0])
            train_indices = np.concatenate((train_indices, resampled_indices), 
                    axis=0)
            return train_indices
        if self.resample_method == 'downsample': 
            true_indices = np.where(self.df[y_col] == True)[0]

            positive_indices = np.intersect1d(true_indices, train_indices)
            negative_indices = np.setdiff1d(train_indices, true_indices)

            resampled_indices = np.random.choice(negative_indices, 
                    positive_indices.shape[0], replace=False)
            train_indices = np.concatenate((positive_indices, resampled_indices),
                    axis=0)
            return train_indices

class SequentialTimeFold(BaseTimeFold):
    """Sequential time fold cross-validation iterator. 

    Provides train/test indices to split the data based 
    off a date or datetime column. The user primarily inputs 
    a dataframe holding a date column, and a step size by which to 
    generate the folds. Folds are then created in a 
    sequential manner, where all obs. on days before the 
    (test_date - step_size) are in the training set, and all 
    obs. on the test_date are in the test set. 

    Inherits from `BaseTimeFold`, and allows the same arguments to 
    be passed in. This builds on `BaseTimeFold` by implementing 
    the `__iter__` method, allowing an instance of this class to
    be used as a generator passed to GridSearchCV. 
    """

    def __init__(self, df, step_size, max_folds, test_set_date, y_col=None, 
            resample_y_pct=None, resample_method=None):
        super(SequentialTimeFold, self).__init__(df, step_size, max_folds, 
                test_set_date, y_col, resample_y_pct, resample_method)

    def next(self):
        """Generate integer indices corresponding to train/test sets. 
        
        At it's first iteration, it simply takes all those observations 
        that are on `self.test_date` as the test set, and all observations
        prior to that in time as the training set. It then generates
        subsequent train/test splits (folds) by stepping back through time 
        by `self.step_size` and performing new splits. It allows for 
        re-sampling of the training indices as discussed in the 
        `_check_resample` method that is built into the `BaseTimeFold` class. 

        Return: 
        ------
            train_indices: np.ndarray
            test_indices: np.ndarray
        """
        
        # Initialize a array with shape 0 so that we can issue the check 
        # every time to make sure that we don't return back a test_indices
        # array with no actual indices. 
        test_indices = np.zeros((0))

        while test_indices.shape[0] == 0: 
            # Define a range of one day for the test date (this was easiest
            # given that the date column has hours/minutes/seconds and strict
            # equality wouldn't work. 
            test_date = self.test_date
            test_date_plus = test_date + timedelta(days=1)

            test_indices = np.where(np.logical_and(self.all_dates >= test_date, 
                self.all_dates < test_date_plus))[0]
            train_indices = np.where(self.all_dates < test_date)[0]
            self.test_date -= self.step_size

            if len(np.unique(self.df.ix[test_indices, self.y_col])) != 2: 
                test_indices = np.zeros((0))
        
        if self.resample_y_pct: 
            # If `self.resample_y_pct` is passed in, then perform re-sampling. 
            training_perc_fire = self.df.ix[train_indices, 'fire_bool'].mean()
            train_indices = self._check_resample(train_indices)
        if self.n_folds <= self.max_folds: 
            self.n_folds += 1
            return train_indices, test_indices
        else: 
            raise StopIteration()

class StratifiedTimeFold(BaseTimeFold):
    """Stratified time  fold cross-validation iterator. 

    Provides train/test indices to split the data based 
    off a date or datetime column. The user primarily inputs 
    a dataframe holding a date column, and a step size by which to 
    generate the folds. Folds are then created in a 
    stratified manner, where all obs. `days_back` number of days before the 
    (test_date - step_size) in the same year and any prior year
    are in the training set, and all obs. on the test_date are 
    in the test set. 

    Inherits from `BaseTimeFold`, and allows the same arguments to 
    be passed in with exception of the `days_back` argument, which 
    tells how many days to go back before `test_date` to grab obs
    for the training data. This builds on `BaseTimeFold` by implementing 
    the `__iter__` method, allowing an instance of this class to
    be used as a generator passed to GridSearchCV. 
    """

    def __init__(self, df, step_size, max_folds, test_set_date, days_back, 
            y_col, resample_y_pct=0.20, resample_method='downsample'):
        super(StratifiedTimeFold, self).__init__(df, step_size, max_folds, 
                test_set_date, y_col, resample_y_pct, resample_method)
        self.years_list = self._set_years_list() 
        self.days_back = days_back

    def _set_years_list(self): 
        """Create a list of years to cycle through. 

        This class will sample some number of `days_back` from
        the `self.test_set_date` in current year as well as all prior
        years, which will require a list of all the years to search
        over. Create that here. 

        Return: 
        ------
            year_list: lst of ints 
        """

        year_max = self.all_dates.max().year
        year_min = self.all_dates.min().year
        year_list = xrange(year_min, year_max + 1)

        return year_list

    def __iter__(self): 
        return self

    def next(self):
        """Generate integer indices corresponding to train/test sets. 
        
        At it's first iteration, it simply takes all those observations 
        that are on `self.test_date` as the test set. For the training
        set, it goes `days_back` in the current year and puts those in it. 
        It then looks at all days in the range (`self.test_date` - self.`days_back`, 
        `self.test_date`) in prior years, and adds those to the test set. 
        
        It then generates subsequent train/test splits (folds) by stepping 
        back through time by `self.step_size` and performing new splits. 
        It allows for re-sampling of the training indices as discussed in the 
        `_check_resample` method that is built into the `BaseTimeFold` class. 

        Return: 
        ------
            train_indices: np.ndarray
            test_indices: np.ndarray
        """
        test_indices, train_indices = np.zeros((0)), np.array([])
        
        while test_indices.shape[0] == 0: 
            test_date = self.test_date
            test_date_plus = test_date + self.step_size 
            test_indices = np.where(np.logical_and(self.all_dates >= test_date, 
                self.all_dates < test_date_plus))[0]
          
            # Now grab all the fires that will be used for training. We'll 
            # have to cycle back through the years to grab these. 
            for year in self.years_list:
                train_idx_temp = self._grab_indices(year)
                train_indices = np.concatenate((train_idx_temp, train_indices))
            training_perc_fire = self.df.ix[train_indices, 'fire_bool'].mean()
            if training_perc_fire < self.cutoff_train_y_pct:  
                train_indices = np.where(self.all_dates < self.test_date)[0]
            self.test_date -= self.step_size

            if len(np.unique(self.df[self.y_col])) != 2: 
                test_indices = np.zeros((0))
        
        training_perc_fire = self.df.ix[train_indices, 'fire_bool'].mean()
        train_indices = self._check_resample(train_indices)
        if self.n_folds <= self.max_folds: 
            self.n_folds += 1
            return train_indices, test_indices
        else: 
            raise StopIteration()

    def _grab_indices(self, year): 
        """Grab the training indices for an inputted year. 

        If it's the current year of the `self.test_date`, grab
        all observations that are within `self.days_back`. If it's
        any prior year, grab any observations within the date range
        of (`self.test_date` - `self.days_back`, `self.test_date` for
        that year. 

        For example, if `self.test_date` is March 13th, 2014 and 
        `self.days_back` is 10, the final training set would include: 
        
            * March 2nd - March 12th, 2014
            * March 3rd - March 13th, 2013
            * March 3rd - March 13th, 2012

        Args: 
        ----
            year: int

        Return: 
        ------
            train_indices: np.ndarray
        """

        date_range = self._get_date_range(year)

        train_indices = np.where((self.all_dates >= date_range.min()) 
                & (self.all_dates < date_range.max()))[0]

        return train_indices

    def _get_date_range(self, year): 
        """Output a `pd.date_range` based off the inputted hear. 

        This is called as a helper function from `self._grab_indices()`, 
        and actually performs the calculations to determine exactly 
        what date range to pull given the year. 
    
        Args: 
        ----
            year: int

        Return: 
        ------
            date_range: pd.date_range
        """

        if year == self.test_date.year: 
            start_date_range = self.test_date
        else: 
            start_date_range = datetime(year, self.test_date.month, 
                    self.test_date.day + 1, 0, 0, 0) 
        end_date_range = start_date_range - timedelta(days=self.days_back)
        date_range = pd.date_range(end_date_range, start_date_range)

        return date_range

