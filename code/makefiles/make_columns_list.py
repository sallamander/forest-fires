import pickle

columns_list = ['lat', 'long', 'gmt', 'temp', 'conf', 'frp', 
        'urban_areas_bool', 'state_fips', 'land_water_ratio', 
        'all_nearby_count0', 'all_nearby_count1', 'all_nearby_count2', 
        'all_nearby_count3', 'all_nearby_count4', 'all_nearby_count5', 
        'all_nearby_count6', 'all_nearby_count7', 'all_nearby_fires1', 
        'all_nearby_fires2', 'all_nearby_fires3', 'all_nearby_fires4', 
        'all_nearby_fires5', 'all_nearby_fires6', 'all_nearby_fires7', 
        'all_nearby_count365', 'all_nearby_fires365', 'all_nearby_count730', 
        'all_nearby_fires730', 'all_nearby_count1095', 'all_nearby_fires1095', 
        'year_2014', 'year_2013', 'year_2012', 'year_2015', 'month_1', 
        'month_2', 'month_3', 'month_4', 'month_5', 'month_6', 'month_7', 
        'month_8', 'month_9', 'month_10', 'month_11', 'month_12', 'date_fire', 'fire_bool']

"""
columns_list = ['lat', 'long', 'frp', 'date_fire', 'fire_bool', 
        'urban_areas_bool', 'land_water_ratio', 'gmt', 'temp', 'conf',
        'all_nearby_fires1', 'all_nearby_fires2', 'all_nearby_fires3', 
        'all_nearby_fires4', 'all_nearby_fires5', 'all_nearby_fires6', 
        'all_nearby_fires7', 'year_2012', 'year_2013', 'year_2014', 
        'year_2015', 'month_1', 'month_2', 'month_3', 'month_4', 'month_5', 
        'month_6', 'month_7', 'month_8', 'month_9', 'month_10', 'month_11', 
        'month_12']
"""

with open('makefiles/columns_list.pkl', 'w+') as f: 
	pickle.dump(columns_list, f)
