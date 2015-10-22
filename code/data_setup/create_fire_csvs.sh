#!bin/bash

# Here I just want to output csvs holding all of the info from the detected
# fires data tables in my forest fires database. 

tbl_years=( 2012 2013 2014 2015 )

for year in "${tbl_years[@]}"
do 
    psql -d forest_fires -c "COPY detected_fires_$year TO \
        '/Users/sallamander/galvanize/forest-fires/data/csvs/detected_fires_$year.csv' \
        WITH CSV HEADER DELIMITER AS E',';"
done 
