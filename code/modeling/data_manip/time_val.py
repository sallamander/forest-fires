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
        
        self.idx = np.arange(self.dates.shape[0])
        self.dates = pd.Series(dates)
        self.step_size = step_size
        self.test_indices = np.array((3, 4))
        if not init_split_point:
            self._set_init_split_point()
            self.split_point = self.init_split_point
        else: 
            self.init_split_point = init_split_point
            self.split_point = self.init_split_point

    def _set_init_split_point(): 
        ''' 
        Assign an initial time-based split point 
        for the first train/test split. 
        '''

        self.init_split_point = dates.min() + self.step_size

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
        test_indices = np.where(self.dates >= self.split_point)[0]
        train_indices = np.where(self.dates < self.split_point)[0]
        self.test_indices = test_indices 
        self.split_point += self.step_size
        
        if self.test_indices.shape[0] != 0: 
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
        super(SequentialTimeFold, self).__init__(dates, step_size, 
                init_split_point)

    def __iter__(self): 
        return self

    def next(self):

        ''' Generates integer indices corresponding to train/test sets. '''
        idx = np.arange(self.dates.shape[0])
        if self.test_indices.shape[0] != 0: 
            split_point = self.split_point
            self.split_point += self.step_size
            test_indices = np.where(self.dates >= self.split_point)[0]
            train_indices = np.where(self.dates < self.split_point)[0]
            self.test_indices = test_indices 
            
            return train_indices, test_indices
        else: 
            raise StopIteration()

def get_df(year): 
    '''
    Input: Integer
    Output: Pandas Dataframe 

    For the given year, read in the detected fires csv to a pandas dataframe, 
    and output it. This function was written just to make the code a little more 
    readable.
    '''

    filepath = '../../../data/csvs/detected_fires_' + str(year) + '.csv'
    df = pd.read_csv(filepath, true_values = ['t'], false_values=['f'], index_col=False)

    return df

if __name__ == '__main__': 
    year_list = [2012, 2013, 2014, 2015]
    dfs_list = [get_df(year) for year in year_list] 
    df = pd.concat(dfs_list, ignore_index=True)
    df = add_date_column(df)
    
    td = timedelta(days=14)
    date = datetime(2014, 1, 1, 0, 0, 0)
    tf = SequentialTimeFold(df['date_fire'], td, date)
