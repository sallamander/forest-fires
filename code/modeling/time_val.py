import numpy as np
import pandas as pd
from datetime import timedelta, datetime

class BaseTimeFold(object):
    ''' 
    Base class for a cross-validation iterator. 

    Setup and prep for the class.
    '''

    def __init__(self, df, step_size, max_folds, test_set_date): 
        ''' Inputs: Pandas DataFrame, Datetime timedelta, Integer''' 
        
        self.n_folds = 0
        self.max_folds = max_folds
        self.df = df
        self.all_dates = df['date_fire'] 
        self.step_size = step_size
        self.test_date = test_set_date - timedelta(days=1)

    def __len__(self): 
        return self.n_folds

class SequentialTimeFold(BaseTimeFold):
    ''' 
    Sequential time fold cross-validation iterator. 

    Provides train/test indices to split the data based 
    off a date or datetime column. The user inputs 
    a numpy array of dates, and a step size by which to 
    generate the folds. 

    Folds are created in a sequential manner, where 
    all obs. on days before the test_date - step_size 
    are in the training set, and all obs. on the test_date 
    are in the test set. 
    '''

    def __init__(self, df, step_size, max_folds, test_set_date): 
        super(SequentialTimeFold, self).__init__(df, step_size, max_folds, 
                test_set_date)

    def __iter__(self): 
        return self

    def next(self):
        ''' Generates integer indices corresponding to train/test sets. '''
        # Initialize a array with shape 0 so that we can issue the check 
        # every time to make sure that we don't return back a test_indices
        # array with no actual indices. 
        test_indices = np.zeros((0))

        while test_indices.shape[0] == 0: 
            test_date = self.test_date
            test_date_plus = test_date + timedelta(days=1)
            test_indices = np.where(np.logical_and(self.all_dates >= test_date, 
                self.all_dates < test_date_plus))[0]
            train_indices = np.where(self.all_dates < test_date)[0]
            self.test_date -= self.step_size
        
        if self.n_folds <= self.max_folds: 
            self.n_folds += 1
            return train_indices, test_indices
        else: 
            raise StopIteration()

class StratifiedTimeFold(BaseTimeFold):
    ''' 
    Stratified time fold cross-validation iterator. 

    Provides train/test indices to split the data based 
    off a date or datetime column. The user inputs 
    a numpy array of dates, and a step size by which to 
    generate the folds. 

    Folds are created in a stratified manner.  
    '''

    def __init__(self, df, step_size, max_folds, test_set_date, days_back, 
            cutoff_train_fire_perc=0.05): 
        super(StratifiedTimeFold, self).__init__(df, step_size, max_folds, 
                test_set_date)
        self.years_list = self._set_years_list() 
        self.days_back = days_back
        self.cutoff_train_fire_perc = cutoff_train_fire_perc

    def _set_years_list(self): 
        ''' 
        Create a list of years to cycle 
        through for the iteration process. 
        '''
        year_max = self.all_dates.max().year
        year_min = self.all_dates.min().year
        year_list = xrange(year_min, year_max + 1)
        return year_list

    def __iter__(self): 
        return self

    def next(self):

        ''' Generates integer indices corresponding to train/test sets. '''
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
            if training_perc_fire < self.cutoff_train_fire_perc:  
                train_indices = np.where(self.all_dates < self.test_date)[0]
                training_perc_fire = self.df.ix[train_indices, 'fire_bool'].mean()
            self.test_date -= self.step_size
            
        if self.n_folds <= self.max_folds: 
            self.n_folds += 1
            return train_indices, test_indices
        else: 
            raise StopIteration()

    def _grab_indices(self, year): 
        '''
        Input: Integer
        Output: Numpy Array, Numpy Array 

        Grab the train and test indices. 
        '''

        date_range = self._get_date_range(year)

        train_indices = np.where((self.all_dates >= date_range.min()) 
                & (self.all_dates < date_range.max()))[0]

        return train_indices


    def _get_date_range(self, year): 
        '''
        Input: Integer
        Output: Pandas DateRange

        Output a date range based off of the current test_date 
        but for the inputted year. The output will be a date range 
        that starts at the test_date (with the year replaced by the 
        inputted year), and goes back by the days_back argument. 
        '''
    
        if year == self.test_date.year: 
            start_date_range = self.test_date
        else: 
            start_date_range = datetime(year, self.test_date.month, 
                    self.test_date.day + 1, 0, 0, 0) 
        end_date_range = start_date_range - timedelta(days=self.days_back)
        date_range = pd.date_range(end_date_range, start_date_range)

        return date_range

