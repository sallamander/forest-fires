"""A module for generating geojson files. 

This module includes functions for generating geojson
files from tables in postgreSQL.
"""

import psycopg2
import json 

def output_json(year, geo_type): 
    """Output a GeoJSON file for inputted year and geo_type.

    Args: 
    ----
        year: int
        geo_type: str
    
    """


    conn = psycopg2.connect(dbname='forest_fires', user=os.environ['USER'])
    cursor = conn.cursor()
            
    query = get_json_query(geo_type, year)

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
    pass
