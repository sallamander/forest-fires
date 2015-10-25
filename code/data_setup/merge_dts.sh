#!/bin/bash

: '
For the fire perimeter boundaries, along with county, state, urban area, and 
region boundaries, we want to know if our detected fire (i.e. its lat/long
coordinates) fall within those boundaries. For some of these (fire 
perimeter, urban area), we just want a boolean of whether or not it 
fell within those boundaries. For the others (county, state, region), 
we want to know what county/state/region it fell in, along with some of 
the other information that is available with those geographies. 

To figure this out, we will take advantage of the POSTGIS extension, 
which will allow us to join two tables, asking whether or not the geography 
from one table (lat/long coordinates) fall within another geography 
(a perimeter boundary). This file will perform all our merging. 
'

# These two varaibles must be passed into the program, and will 
# determine what tables end up getting merged. 
boundary_type=$1
year=$2

if [ "$boundary_type" = "fire" ] || [ "$boundary_type" = "urban_areas" ] 
then 
    label=false
else 
    label=true
fi  

if $label
then
    land=${boundary_type}_aland
    water=${boundary_type}_awater 
    name=${boundary_type}_name
    lsad=${boundary_type}_lsad

    columns_to_add="$land, $water, $name, $lsad"
    polys_keep_columns="polys.aland as $land, polys.awater as $water, \
                        polys.name as $name, polys.lsad as $lsad"

    if [ "$boundary_type" = "region" ] 
    then 
        polys_keep_columns="${polys_keep_columns} , polys.regionce as region_code"
        columns_to_add="${columns_to_add}, region_code"
    else 
        polys_keep_columns="${polys_keep_columns}, polys.${boundary_type}fp as \
                            ${boundary_type}_fips"
        columns_to_add="${columns_to_add}, ${boundary_type}_fips"
    fi
    
    query="CREATE TABLE detected_fires_$year2 AS \
            (WITH \
                distinct_to_merge AS \
                    (SELECT DISTINCT ON (lat, long) * \
                    FROM detected_fires_$year), \
                merged AS \
                    (SELECT DISTINCT points.lat, points.long, ${polys_keep_columns} \
                    FROM distinct_to_merge as points \
                    INNER JOIN ${boundary_tbl} as polys \
                        ON ST_WITHIN(points.wkb_geometry, polys.wkb_geometry)) \
                        \
            SELECT df.*, ${columns_to_add} \
            FROM detected_fires_$year \
            LEFT JOIN merged \
                ON df.lat = merged.lat \
                AND df.long = merged.long); \
        "

else 
    echo notlabel
fi 
