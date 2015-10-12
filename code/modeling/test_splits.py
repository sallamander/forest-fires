import pickle
import sys
import datetime
import pandas as pd
from data_manip.tt_splits import tt_split_all_less_n_days, tt_split_early_late, tt_split_same_months


if __name__ == '__main__': 
	with open(sys.argv[1]) as f: 
		input_df = pickle.load(f)

	days_back = 60
	train, test = tt_split_all_less_n_days(input_df, days_back=days_back)
        train.loc[:, 'date_fire'] = pd.to_datetime(train['date_fire'].copy())

	for months_forward in xrange(0, 78, 2): 
                date_split = train.date_fire.max() - datetime.timedelta(weeks=months_forward)
                training_set, validation_set = tt_split_same_months(train, 2013, [1], days_back=14, exact_split_date = date_split, direct_prior_days=False, add_test=True)

                # training_set, validation_set = tt_split_early_late(train, date_split, months_forward, months_backward=None, days_forward=2, weeks_forward=months_forward)
                print months_forward
                for year in training_set.year.unique(): 
                        print training_set.query('year == @year').date_fire.min(), training_set.query('year == @year').date_fire.max()
                print 'on to validation'
                for year in validation_set.year.unique(): 
                        print validation_set.query('year == @year').date_fire.min(), validation_set.query('year == @year').date_fire.max()
                print '\n' * 2

                '''
                print training_set.date_fire.min(), training_set.date_fire.max()
                print validation_set.date_fire.min(), validation_set.date_fire.max()
                print training_set.fire_bool.sum(), validation_set.fire_bool.sum()
                print '\n' * 2
                '''
