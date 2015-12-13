import numpy as np
import pandas as pd
from datetime import timedelta, datetime
from time_featurization import add_date_column

class BaseTimeFold(object):
    ''' 
    Base class for a cross-validation iterator. 

    Setup and prep for the class.
    '''

    def __init__(self, dates, step_size, init_split_point=None): 
        ''' Inputs: NumpyArray, Datetime timedelta, Datetime datetime ''' 
        
        self.n_folds = 0
        self.dates = pd.Series(dates)
        self.step_size = step_size
        self.test_indices = np.array((3, 4))
        if not init_split_point:
            self._set_init_split_point()
            self.split_point = self.init_split_point
        else: 
            self.init_split_point = init_split_point
            self.split_point = self.init_split_point

    def _set_init_split_point(self): 
        ''' 
        Assign an initial time-based split point 
        for the first train/test split. 
        '''
        
        exact_init_split_point = self.dates.min() + self.step_size
        # We need to round this to midnight so that we don't get 
        # obs. on the same day in the train and test sets. 
        self.init_split_point = datetime(exact_init_split_point.year, 
                        exact_init_split_point.month, exact_init_split_point.day, 
                        0, 0, 0)
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
    all dates before the split_point + step_size are 
    in the training folds, and all dates after are in 
    the test folds. 
    '''

    def __init__(self, dates, step_size, init_split_point=None): 
        super(SequentialTimeFold, self).__init__(dates, step_size, 
                init_split_point)

    def __iter__(self): 
        return self

    def next(self):
        ''' Generates integer indices corresponding to train/test sets. '''
        split_point = self.split_point
        print split_point, self.n_folds
        test_indices = np.where(self.dates >= self.split_point)[0]
        train_indices = np.where(self.dates < self.split_point)[0]
        self.test_indices = test_indices 
        self.split_point += self.step_size
        
        if self.test_indices.shape[0] != 0: 
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

    def __init__(self, dates, step_size, init_split_point=None): 
        super(StratifiedTimeFold, self).__init__(dates, step_size, 
                init_split_point)
        self.years_list = self._set_years_list() 

    def _set_years_list(self): 
        ''' 
        Create a list of years to cycle 
        through for the iteration process. 
        '''
        year_max = self.dates.max().year
        year_min = self.dates.min().year
        year_list = xrange(year_min, year_max + 1)
        return year_list

    def __iter__(self): 
        return self

    def next(self):

        ''' Generates integer indices corresponding to train/test sets. '''
        idx = np.arange(self.dates.shape[0])
        test_indices, train_indices = np.array([]), np.array([])
        
        if self.test_indices.shape[0] != 0: 
            self.n_folds += 1
            for year in self.years_list:
                train_idx_temp, test_idx_temp = self._grab_indices(year)
                train_indices = np.concatenate((train_idx_temp, train_indices))
                test_indices = np.concatenate((test_idx_temp, test_indices))
            self.split_point += self.step_size
            self.test_indices = test_indices 
            
            return train_indices, test_indices
        else: 
            raise StopIteration()

    def _grab_indices(self, year): 
        '''
        Input: Integer
        Output: Numpy Array, Numpy Array 

        Grab the train and test indices. 
        '''

        split_point = self.split_point
        date_range = self._get_date_range(year)

        test_indices = np.where((self.dates >= date_range.min()) 
                & (self.dates < date_range.max()) 
                & (self.dates >= split_point))[0]
        train_indices = np.where((self.dates >= date_range.min()) 
                & (self.dates < date_range.max()) 
                & (self.dates < split_point))[0]

        return train_indices, test_indices


    def _get_date_range(self, year): 
        '''
        Input: Integer
        Output: Pandas DateRange

        Output a date range based off of the current split
        point plus step size, but for the inputted year. The 
        output will be a date range that starts at the current 
        split point (with the year replaced by the inputted year), 
        and extends by the step size. 
        '''

        start_date_range = datetime(year, 
                self.split_point.month, self.split_point.day, 
                self.split_point.hour, self.split_point.minute, 
                self.split_point.second)
        end_date_range = start_date_range + self.step_size
        date_range = pd.date_range(start_date_range, end_date_range)

        return date_range

