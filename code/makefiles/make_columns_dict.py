"""A tiny script for creating pickle dictionaries for feature engineering.

This module simply pickles dictionaries where the keys correspond to columns
of the original data to then apply a function to generate some new kind of 
feature. The values are dictionaries that correspond to what function to apply 
(the `transformation`) and how exactly to apply it. 
"""
import pickle

time_transforms_dict = {'year': {'transformation': 'all_dummies', 
                                 'col': 'year'}, 
                        'month': {'transformation': 'all_dummies', 
                                  'col': 'month'}, 
                        'sat_src': {'transformation': 'all_dummies', 
                                  'col': 'sat_src'}, 
                        'src': {'transformation': 'all_dummies', 
                                  'col': 'src'}
                       }

geo_transforms_dict = {'land_water_ratio': {'transformation': 'create_new_col', 
                                'eval_string': 'county_aland / county_awater', 
                                'delete_columns': ['county_aland', 'county_awater'], 
                                'new_col_name': 'land_water_ratio'}, 
                        'add_nearby_fires': {'dist_measure': 0.1, 
                                'time_measures' : [0, 1, 2, 3, 4, 5, 6, 7, 
                                    365, 730, 1095], 
                                'transformation' : 'add_nearby_fires'}
                      }

with open('code/makefiles/time_transforms_dict.pkl', 'w+') as f: 
    pickle.dump(time_transforms_dict, f)

with open('code/makefiles/geo_transforms_dict.pkl', 'w+') as f: 
    pickle.dump(geo_transforms_dict, f) 
