import pickle
import psycopg2
import time
import os
import sys

class BoundaryMerge(Object): 
    '''
    For the given boundary type, this class will check if each row in the 
    detected fires data table (i.e. a detected fire) is within the perimeter
    boundary for the inputted boundary_type. Depending on the type, 
    it will either just output a boolean that tells us if it fell within 
    that perimeter boundary (fire perimeter boundary and urban area boundary), 
    or a number of variables that contain information for what boundary 
    it fell within (state, county, etc.). These 'output' variables will 
    simply be added to the detected_fires data table so that we can use 
    them later. 
    '''

    def __init__(boundary_type, year): 
        '''
        Input: String, Integer
        '''
        self.year = year
        self.boundary_type = boundary_type

    def conduct_merge(self): 
        self._prep_table_names()
        self._assign_query_type()
        self._handle_connection(close=False)

        query = self._generate_query()
        self.cursor.execute(query)
        self._handle_connection(close=True)

    def _prep_table_names(self): 
        '''
        Input: None
        Output: Two strings assigned as variables to self.  

        Here, we will assign what detected fires table we are using (here 
        we just need to take into account the year). We will also assign
        what boundary table we are using, based off of the self.boundary_type
        variable. 
        '''

        self.detected_fires_table = 'detected_fires_' + self.year
        if year not in (2012, 2015): 
            self.boundary_table = self.boundary_type + '_shapefiles_' + self.year
        
        # The boundary shapefiles are only available for 2013 and 2014. So 
        # we'll use the closest year for 2012 and 2015. 
        if year == 2012: 
            self.boundary_table = self.boundary_type + '_shapefiles_' + str(2013)
        if year == 2015: 
            self.boundary_table = self.boundary_type + '_shapefiles_' + str(2014)

    def _assign_query_type(self): 
        '''
        Input: None
        Output: Assgined boolean. 

        Depending on what type of boundary we are checking against, we will 
        want different information. If all we want is a boolean variable, then 
        we'll set the self.label variable equal to false (i.e. we don't want 
        a label). If we want more information, such as what state/county it is 
        in, we'll set self.label equal to true (i.e. we want a label)
        '''

        boolean = {'fire_perimeters', 'urban'}

        if self.boundary_table in boolean: 
            self.label = False
        else: 
            self.label = True

    def _handle_connection(self, close=False): 
        '''
        Input: None, Boolean
        Output: Assigned connection and cursor object. 

        Open/Close a connection to our database, and create/delete
        a cursor object. Assign both to self so that we don't have 
        to pass these back and forth across functions. 
        '''
        
        if close: 
            self.cursor.close()
            self.conn.close()
        else: 
            self.conn = psycopg2.connect(dbname='forest_fires', user=os.environ['USER'])
            self.cursor = self.conn.cursor()

    def _generate_query(self): 
        '''
        Input: None
        Output: String

        Given the detected fires table name, the boundary file table name, and
        whether or not we want labels or a simple boolean, return a query string
        that we can get our label (and other info) or our simple boolean.
        '''

        if self.label: 
            query = self._create_label_query()
        else: 
            query = self._create_bool_query()

        return query

    def _create_label_query(self): 
        '''
        Input: None
        Output: String

        Actually generate the query string, provided that we want the label of the
        boundary that the detected fire falls in, and not just a boolean of 
        whether it falls in that boundary. We'll also grab some of the other 
        variables that come with that boundary (land area, water area, etc.). 

        Notes: This might not be the cleanest way of doing this, but I spent some 
        time trying to use ALTER TABLE table update and/or INSERT INTO, and 
        neither really panned out. This works, and it's only being run a handful 
        of times, so I'm not terribly worried at this moment, but would like to 
        know if there is a better way to do this. 
        '''

        land, water, name, lsad = self.boundary_type + 'a_land',
                                    self.boundary_type + '_water', 
                                    self.boundary_type + '_name', 
                                    self.boundary_type + '_lsad'

        polys_keep_columns = '''polys.aland as {}, polys.awater as {}, 
                                polys.name as {}, polys.lsad as {}
                             '''.format(land, water, name, lsad)

        columns_to_add = [land, water, name, lsad]
        
        if self.boundary_type == 'region': 
            polys_keep_columns += ', polys.regionce as region_code'
            columns_to_add.append('region_code')
        else: 
            polys_keep_columns += ', polys' + self.boundary_type + 'fp as ' \
                                  self.boundary_type + '_fips'
            columns_to_check.append(self.boundary_type + '_fips')

        query = '''CREATE TABLE {detected_fires_table}2 AS 
                        (WITH 
                            distinct_to_merge AS 
                                (SELECT DISTINCT ON (lat, long) *
                            merged AS 
                                (SELECT DISTINCT points.lat, points.long, 
                                        {polys_keep_columns}
                                 FROM distinct_to_merge as points
                                 INNER JOIN {shapefile_table_name} as polys
                                    ON ST_WITHIN(points.wkb_geometry, 
                                                 polys.wkb_geometry))
                        
                        SELECT df.*, {columns_to_add}
                        FROM {detected_fires_table} df
                        LEFT JOIN merged 
                            ON df.lat = merged.lat 
                            AND df.long = merged.long
                        );'''.format(detected_fires_table=self.detected_fires_table, 
                                     shapefile_table_name=self.shapefile_table_name, 
                                     polys_keep_columns=polys_keep_columns, 
                                     columns_to_add=columns_to_add)
        return query
    
    def _create_bool_query(self):
        '''
        Input: None 
        Output: String 

        Generate the query string, provided we know we want a boolean of 
        whether or not the lat/long coordinate for a detected fire 
        falls within the perimter boundary or not (and thats it).
        '''

        on_query_part = 'ST_WITHIN(points.wkb_geometry, polys.wkb_geometry)' 
        select_distinct_on = '(lat, long)' 
        bool_col_name = self.boundary_type + '_bool'

        if self.boundary_type == 'fire_bool': 
            on_query_part += ' AND points.date = polys.date_'
            select distinct_on = ('lat, long, date')

        # Breakdown of this query... kind of from the inside out... 
        # 
        # 1.) Merge the detected fires data with whater shapefile we want, 
        # and keep track of only the unique late, long, and date in a temporary
        # table. 
        # 2.) Merge the detected fires data table with merged and along the 
        # way create a boolean that holds whether each row of the detected fires
        # data table was within the shape perimeter boundary. 
        # 3.) Create a new table holding these results. 
        #
        # The create_label_query works almost exactly like this, but returns 
        # different columns from the query (labelish columns, not a boolean). 

        query = '''CREATE TABLE {detected_fires_table}2 AS
                    (WITH 
                        distinct_to_merge AS 
                            (SELECT DISTINCT ON {select_distinct_on} * 
                             FROM {detected_fires_table}), 
                        merged AS 
                            (SELECT DISTINCT points.lat, points.long, points.date
                             FROM distinct_to_merge as points
                             INNER JOIN {shapefile_table_name} as polys
                                ON {on_query_part})

                    SELECT df.*, 
                        CASE WHEN merged.lat IS NOT NULL THEN TRUE
                             WHEN merged.lat IS NULL THEN FALSE END AS {bool_col_name}
                        FROM {detected_fires_table} df
                        LEFT JOIN merged
                            ON df.lat = merged.lat
                            AND df.long = merged.long
                            AND df.date = merged.date);
                '''.format(detected_fires_table=self.detected_fires_table, 
                            shapefile_table_name=self.shapefile_table_name, 
                            bool_col_name=bool_col_name,
                            on_query_part=on_query_part, 
                            select_distinct_on=select_distinct_on)

        return query 
