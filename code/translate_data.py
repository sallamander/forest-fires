import reverse_geocoder as rg
import simplejson
import pickle
from requests import get
from collections import defaultdict

def get_reverse_geocode(df): 
	'''
	Input: Pandas DataFrame
	Output: Pandas DataFrame

	Take the latitude/longitude coordinates for each row in the DataFrame, and get the country, state, 
	and county information and put those in the DataFrame. 
	'''

	print 'In Reverse Geocode'

	geo_info = defaultdict(list)
	for idx, lat in enumerate(df['LAT']): 
		coords = (lat, df.loc[idx, 'LONG'])
		results = rg.search(coords)[0]


		geo_info['country'].append(results['cc'])
		geo_info['state'].append(results['admin1'])
		geo_info['county'].append(results['admin2'])


	df['country'] = geo_info['country']
	df['state'] = geo_info['state']
	df['county'] = geo_info['county']

	return df

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



