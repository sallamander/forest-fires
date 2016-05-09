#!/bin/bash 

# This will grab fire perimeter boundaries for 
# a given state and date. 

st_name=$1
st_fips=$2
dt=$3
cnty_name=$4

if [ ! -d data/${st_name} ]; then 
    mkdir -p data/${st_name}
fi 


year=${dt:0:4}

if [ ! -z ${cnty_name} ]; then 
    ogr2ogr -f "ESRI Shapefile" ${st_name}_${cnty_name}_${dt}.shp PG:"host=localhost user=sallamander dbname=forest_fires" -sql "SELECT wkb_geometry FROM fp_cnts_${year} WHERE statefp = '${st_fips}' and name = '${cnty_name}' and date_ = '${dt}';"
    mv ${st_name}_${cnty_name}_${dt}.* data/cnty_exploration/
    ogr2ogr -f "ESRI Shapefile" -dim 2 data/cnty_exploration/${st_name}_${cnty_name}_${dt}_2D.shp data/cnty_exploration/${st_name}_${cnty_name}_${dt}.shp 
    rm data/cnty_exploration/${st_name}_${cnty_name}_${dt}.*
else
    if [ ! -f data/${st_name}/${st_name}_${dt}_2D.shp ]; then 
        if [ ${#dt} -gt 5 ]; then 
            ogr2ogr -f "ESRI Shapefile" ${st_name}_${dt}.shp PG:"host=localhost user=sallamander dbname=forest_fires" -sql "SELECT wkb_geometry FROM fp_sts_${year} WHERE statefp = '${st_fips}' and date_ = '${dt}';"
            mv ${st_name}_${dt}.* data/${st_name}/
            ogr2ogr -f "ESRI Shapefile" -dim 2 data/${st_name}/${st_name}_${dt}_2D.shp data/${st_name}/${st_name}_${dt}.shp 
            rm data/${st_name}/${st_name}_${dt}.*
        else 
            ogr2ogr -f "ESRI Shapefile" ${st_name}_${dt}.shp PG:"host=localhost user=sallamander dbname=forest_fires" -sql "SELECT wkb_geometry FROM fp_sts_${year} WHERE statefp = '${st_fips}';"
            mv ${st_name}_${dt}.* data/${st_name}/
            ogr2ogr -f "ESRI Shapefile" -dim 2 data/${st_name}/${st_name}_${dt}_2D.shp data/${st_name}/${st_name}_${dt}.shp 
            rm data/${st_name}/${st_name}_${dt}.* 
        fi 
    fi 
fi 
