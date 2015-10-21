#!bin/bash

# In this file read in and create data tables in our forest_fires database
# for all of our shapefiles. 
 
# The fire boundaries and detected fires are available for 2012-2015, 
# where as the other boundary files are only available for 2013-2014. 

fire_tbl_years=( 2012 2013 2014 2015 ) 
boundary_tbl_years=( 2013 2014 )
non_fire_boundaries=( county state urban region )

for year in "${fire_tbl_years[@]}"
do
    ogr2ogr -f "PostgreSQL" PG:"dbname=forest_fires user="$USER \
        "../../data/unzipped_files/detected_fires/MODIS/"$year/ \
        -nlt PROMOTE_TO_MULTI -nln detected_fires_$year -overwrite 

    ogr2ogr -f "PostgreSQL" PG:"dbname=forest_fires user="$USER \
        "../../data/unzipped_files/boundary_files/fire_perimeters"$year/ \
        -nlt PROMOTE_TO_MULTI -nln fire_perimeters_$year -overwrite 
done 

for year in "${boundary_tbl_years[@]}"
do 
    for tbl_name in "${non_fire_boundaries[@]}"
    do 
        ogr2ogr -f "PostgreSQL" PG:"dbname=forest_fires user="$USER \
            "../../data/unzipped_files/boundary_files/"${tbl_name}/$year/ \
            -nlt PROMOTE_TO_MULTI -nln ${tbl_name}_perimeters_$year -overwrite 
    done 
done 

