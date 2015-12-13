#!bin/bash

for opt in $@
do 
    case $opt in 
        -c)   
            # First create our database and add the POSTGIS extension. We'll need
            # this for any of the options that follow.
            psql postgres -c "CREATE DATABASE forest_fires;"
            psql -d forest_fires -c "CREATE EXTENSION POSTGIS;"
            exit 
            ;; 
        -r) 
            # In this file read in and create data tables in our forest_fires database
            # for all of our shapefiles. 
             
            # The fire boundaries and detected fires are available for 2012-2015, 
            # where as the other boundary files are only available for 2013-2014. 

            fire_tbl_years=( 2012 2013 2014 2015 ) 
            boundary_tbl_years=( 2013 2014 )
            non_fire_boundaries=( county state urban_areas region )

            for year in "${fire_tbl_years[@]}"
            do
                ogr2ogr -f "PostgreSQL" PG:"dbname=forest_fires user="$USER \
                    "data/unzipped_files/detected_fires/MODIS/"$year/ \
                    -nlt PROMOTE_TO_MULTI -nln detected_fires_$year -overwrite 

                ogr2ogr -f "PostgreSQL" PG:"dbname=forest_fires user="$USER \
                    "data/unzipped_files/boundary_files/fire_perimeters"/$year/ \
                    -nlt PROMOTE_TO_MULTI -nln fire_perimeters_$year -overwrite 
            done 

            for year in "${boundary_tbl_years[@]}"
            do 
                for tbl_name in "${non_fire_boundaries[@]}"
                do 
                    if [ "$tbl_name" = "state" ]  
                    then 
                        ogr2ogr -f "PostgreSQL" PG:"dbname=forest_fires user="$USER \
                            "data/unzipped_files/boundary_files/"${tbl_name}/$year/ \
                            -nlt PROMOTE_TO_MULTI -nln ${tbl_name}_perimeters_$year -overwrite 
                    else 
                        PGCLIENTENCODING=LATIN1 ogr2ogr -f "PostgreSQL" \
                            PG:"dbname=forest_fires user="$USER \
                            "data/unzipped_files/boundary_files/"${tbl_name}/$year/ \
                            -nlt PROMOTE_TO_MULTI -nln ${tbl_name}_perimeters_$year -overwrite 
                    fi 
                done 
            done 
            exit 
            ;; 
        -o)
            # Here I just want to output csvs holding all of the info from the detected
            # fires data tables in my forest fires database. 

            tbl_years=( 2012 2013 2014 2015 )

            for year in "${tbl_years[@]}"
            do 
                psql -d forest_fires -c "COPY detected_fires_$year TO \
                    '$PWD/data/csvs/detected_fires_$year.csv' \
                    WITH CSV HEADER DELIMITER AS E',';"
            done 
            exit 
            ;; 
        -m) 
            shift 1; 
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

            boundary_tbl=${boundary_type}_perimeters_$year

            # The boundary shapefiles for all but the fire perimters 
            # are only available for 2013 and 2014. So we'll use the closest
            # year for 2012 and 2015 (which is 2013 and 2014). 
            if [ "$boundary_type" != "fire" ] 
            then 
                if [ "$year" = "2012" ] 
                then 
                    boundary_tbl=${boundary_type}_perimeters_2013
                elif [ "$year" = "2015" ] 
                then 
                    boundary_tbl=${boundary_type}_perimeters_2014
                fi 
            fi

            echo $boundary_tbl
                
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
                
                query="CREATE TABLE detected_fires_${year}2 AS \
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
                        FROM detected_fires_$year df \
                        LEFT JOIN merged \
                            ON df.lat = merged.lat \
                            AND df.long = merged.long); \
                    "
            else 
                on_query_part="ST_WITHIN(points.wkb_geometry, polys.wkb_geometry)"
                select_distinct_on="(lat, long)"
                bool_col_name=${boundary_type}_bool

                # If we are looking at the fire perimeters, then we'll be merging on date
                # and geometry. 
                if [ "$boundary_type" = "fire" ]
                then 
                    on_query_part="${on_query_part} AND points.date = polys.date_"
                    select_distinct_on="(lat, long, date)"
                fi 

                query="CREATE TABLE detected_fires_${year}2 AS \
                        (WITH \
                            distinct_to_merge AS \
                                (SELECT DISTINCT ON ${select_distinct_on} * \
                                FROM detected_fires_$year), \
                        merged AS \
                            (SELECT DISTINCT points.lat, points.long, points.date \
                            FROM distinct_to_merge as points \
                            INNER JOIN ${boundary_tbl} as polys \
                                ON ${on_query_part}) \
                                \
                        SELECT df.*, \
                            CASE WHEN merged.lat IS NOT NULL THEN TRUE \
                                WHEN merged.lat IS NULL THEN FALSE END AS ${bool_col_name} \
                            FROM detected_fires_$year df \
                            LEFT JOIN merged \
                                ON df.lat = merged.lat \
                                AND df.long = merged.long \
                                AND df.date = merged.date); 
                    " 
            fi 

            psql -d forest_fires -c "$query"
            psql -d forest_fires -c "DROP TABLE detected_fires_$year;"
            psql -d forest_fires -c "ALTER TABLE detected_fires_${year}2 \
                                    RENAME to detected_fires_$year;"
            exit 
            ;;
    esac
done 

