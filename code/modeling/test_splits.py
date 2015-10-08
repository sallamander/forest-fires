import pickle
import sys
from data_manip.tt_splits import tt_split_all_less_n_days, tt_split_early_late


if __name__ == '__main__': 
	with open(sys.argv[1]) as f: 
		input_df = pickle.load(f)

	days_back = 60
	train, test = tt_split_all_less_n_days(input_df, days_back=days_back)

	for months_forward in xrange(0, 31, 3): 
		training_set, validation_set = tt_split_early_late(train, 2012, months_forward, months_backward=13)
		print training_set.date_fire.min(), training_set.date_fire.max()
		print validation_set.date_fire.min(), validation_set.date_fire.max()
		print '\n' * 2