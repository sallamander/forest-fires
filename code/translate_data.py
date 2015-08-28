import reverse_geocoder as rg
import simplejson
import pickle
from requests import get
from collections import defaultdict

def get_weather_data(): 
	'''
	Input: Pandas DataFrame
	Output: 

	Take the latitude/longitude and time data for each row in the DataFrame, and get the weather 
	for that pairing. I want to go three days back in time for each row in the DataFrame. 
	'''

	with open('/Users/sallamander/apis/access/forecast_io.json') as f: 
		pass 
	return file_json


if __name__ == '__main__': 
	for year in xrange(2015, 2012, -1):
		with open('../../data/pickled_data/MODIS/df_' + str(year) + '.pkl') as f: 
			df = pickle.load(f)
			df = get_reverse_geocode(df)
			print 'Finished Year... ' + str(year)
			with open('../../data/pickled_data/MODIS/df_' + str(year) + '_st.pkl', 'w+') as f2: 
				pickle.dump(df, f2)



