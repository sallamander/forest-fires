"""A module for generating geojson files. 

This module includes functions for generating geojson
files from tables in postgreSQL.
"""

import os
import pandas as pd
import psycopg2
import json 

def output_json(year, geo_type): 
    """Output a GeoJSON file for inputted year and geo_type.

    Given an inputted year and geography type, query the correct
    postgres table for the right geometries. Then, read those into
    a DataFrame, iterate through each row to format it for output, 
    and output the final formatted data in a GeoJson file. 

    Args: 
    ----
        year: int
        geo_type: str
    """


    conn = psycopg2.connect(dbname='forest_fires', user=os.environ['USER'])
            
    query = get_json_query(year, geo_type)
    query_df = pd.read_sql(query, conn)

    list_to_export = [add_geo_properties(row[1]) for row \
            in query_df.iterrows()]
    return list_to_export

def get_json_query(year, geo_type): 
    """Format a query for the inputted year and geo_type. 

    Args: 
    ----
        year: int
        geo_type: str

    Return: 
    ------
        query: str
            Holds the query to issue from the pyscopg2 cursor object. 
    """

    from_table = geo_type + '_perimeters_' + str(year)
    select_variables = 'DISTINCT ST_AsGeoJSON(wkb_geometry) as geometry, name'

    query = '''SELECT {select_variables} 
                            FROM {from_table};
                    '''.format(select_variables=select_variables, 
                               from_table=from_table)

    return query

def add_geo_properties(row): 
    """Format the inputted row to match the GeoJSON specification.

    The GeoJSON specification expects each "feature" object (which is what
    a row passed in is) to have the following: 

    * A member with the name "geometry"
    * A member with the name "properties"

    This function formats the inputted row to meet that specification. 

    Args: 
    ----
        row: pandas Series 
            Each row is returned from the result of a `.iterrows()` call on 
            the pandas DataFrame. 
    """

    properties_dict = {}
    properties_dict['name'] = row['name']

    geo_json = {"type": "Feature", "geometry": json.loads(row['geometry']),  "properties": properties_dict} 
    
    return geo_json
