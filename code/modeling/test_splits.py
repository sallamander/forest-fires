import pickle
import sys
from data_manip.tt_splits import tt_split_all_less_n_days, tt_split_early_late, tt_split_same_months


if __name__ == '__main__': 
	with open(sys.argv[1]) as f: 
		input_df = pickle.load(f)

	days_back = 60
	train, test = tt_split_all_less_n_days(input_df, days_back=days_back)

	for months_forward in xrange(0, 31, 2): 
                '''
                training_set, validation_set = tt_split_same_months(train, 2013, [months_forward, months_forward + 1])
                '''
                training_set, validation_set = tt_split_early_late(train, 2012, months_forward, months_backward=7, year=True, days_forward=60)
                '''
                print training_set.month.unique(), training_set.year.unique()
                print validation_set.month.unique(), validation_set.year.unique()
                print training_set.fire_bool.sum(), validation_set.fire_bool.sum()
                print '\n' * 2
                '''

                print training_set.date_fire.min(), training_set.date_fire.max()
                print validation_set.date_fire.min(), validation_set.date_fire.max()
                print training_set.fire_bool.sum(), validation_set.fire_bool.sum()
                print '\n' * 2
