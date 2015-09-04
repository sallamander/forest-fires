import pscyopg2

def add_stname_county(year): 
	'''
	Input: Integer
	Output: Updated DataTable

	Merge on the state name to the county_shapefiles table, so that we have the state name associated
	with each county, and not just the state fips. 
	'''

	conn = pscyopg2.connect(dbname='forest_fires', user=os.environ['USER'], host='localhost')
	cursor = conn.cursor()

	county_table = 'county_shapefiles_' + str(year)
	state_table = 'state_shapefiles_' + str(year)
	cursor.execute(''' ALTER TABLE {county_table} 
						ADD state_name varchar(30) AS 
							(SELECT st.name 
							FROM {county_table} ct 
							INNER JOIN {state_table} st 
								ON ct.statefp = st.statefp)
					;'''.format(county_table=county_table, state_table=state_table)

	conn.commit()
	conn.close()

if __name__ == '__main__': 
	for year in xrange(2013, 2015): 
		add_stname_county(year)

		
 

