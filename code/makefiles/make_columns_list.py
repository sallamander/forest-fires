"""A tiny script to pickle the list of columns to include in the models being run."""
import pickle

columns_list = [u'lat', u'long', u'gmt', u'temp', u'spix', u'tpix',
                u'conf', u'frp', u'fire_bool', u'urban_areas_bool',
                u'region_aland', u'region_awater', u'region_lsad',
                u'county_lsad', u'state_aland', u'state_awater', 
                u'state_lsad', u'date_fire', u'land_water_ratio',
                u'all_nearby_count0', u'all_nearby_fires0', 
                u'all_nearby_count1', u'all_nearby_fires1',
                u'all_nearby_count2', u'all_nearby_fires2', 
                u'all_nearby_count3', u'all_nearby_fires3', 
                u'all_nearby_count4', u'all_nearby_fires4',
                u'all_nearby_count5', u'all_nearby_fires5', 
                u'all_nearby_count6', u'all_nearby_fires6', 
                u'all_nearby_count7', u'all_nearby_fires7',
                u'all_nearby_count365', u'all_nearby_fires365',
                u'all_nearby_count730', u'all_nearby_fires730',
                u'all_nearby_count1095', u'all_nearby_fires1095', 
                u'perc_fires0', u'perc_fires1', u'perc_fires2',
                u'perc_fires3', u'perc_fires4', u'perc_fires5', 
                u'perc_fires6', u'perc_fires7', u'perc_fires365', 
                u'perc_fires730', u'perc_fires1095', u'sat_src_A', u'sat_src_T',
                u'src_gsfc', u'src_gsfc_drl', u'src_rsac', u'src_ssec', u'src_uaf',
                u'year_2012', u'year_2013', u'year_2014', u'year_2015', u'month_1',
                u'month_2', u'month_3', u'month_4', u'month_5', u'month_6',
                u'month_7', u'month_8', u'month_9', u'month_10', u'month_11',
                u'month_12']

with open('code/makefiles/columns_list.pkl', 'w+') as f: 
	pickle.dump(columns_list, f)
