import pickle

time_transforms_dict = {'year': {'transformation': 'all_dummies', 
                                 'col': 'year'}, 
                        'month': {'transformation': 'all_dummies', 
                                  'col': 'month'}
                       }

geo_transforms_dict = {'land_water_ratio': {'transformation': 'create_new_col', 
                                'eval_string': 'county_aland / county_awater', 
                                'delete_columns': ['county_aland', 'county_awater'], 
                                'new_col_name': 'land_water_ratio'}, 
                        'add_nearby_fires': {'dist_measure': 0.1, 
                                'time_measures' : [0, 1, 2, 3, 4, 5, 6, 7], 
                                'transformation' : 'add_nearby_fires'}
                      }

with open('makefiles/time_transforms_dict.pkl', 'w+') as f: 
    pickle.dump(time_transforms_dict, f)

with open('makefiles/geo_transforms_dict.pkl', 'w+') as f: 
    pickle.dump(geo_transforms_dict, f) 
