import reverse_geocoder as rg

def get_reverse_geocode(df): 
	'''
	Input: Pandas DataFrame
	Output: Pandas DataFrame

	Take the latitude/longitude coordinates for each row in the DataFrame, and get the country, state, 
	and county information and put those in the DataFrame. 
	'''

	geo_info = defaultdict(list)
	df = df.loc[0:50].copy()
	for idx, lat in enumerate(df['LAT']): 
		coords = (lat, df.loc[idx, 'LONG'])
		print idx, coords
		results = rg.search(coords)[0]


		geo_info['country'].append(results['cc'])
		geo_info['state'].append(results['admin1'])
		geo_info['county'].append(results['admin2'])


	df['country'] = geo_info['country']
	df['state'] = geo_info['state']
	df['county'] = geo_info['county']

	return df