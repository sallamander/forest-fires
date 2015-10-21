#!/bin/bash

mkdir zipped_files 
mkdir unzipped_files 

in_zip_unzip_files=( boundary_files detected_fires )
in_boundary_files=( county fire_perimeters region state urban_areas )
in_detected_fires=( MODIS )
fire_tbl_years=( 2012 2013 2014 2015 ) 
boundary_tbl_years=( 2013 2014 )


for folder_name in "${in_zip_unzip_files[@]}"
do 
    mkdir zipped_files/$folder_name
    mkdir unzipped_files/$folder_name
done 

for folder_name in "${in_boundary_files[@]}"
do 
    mkdir zipped_files/boundary_files/$folder_name
    mkdir unzipped_files/boundary_files/$folder_name
    if [ "$folder_name" = "fire_perimeters" ]  
    then
        for year in "${fire_tbl_years[@]}"
        do 
            mkdir unzipped_files/boundary_files/$folder_name/$year
        done 
    else 
        for year in "${boundary_tbl_years[@]}"
        do 
            mkdir unzipped_files/boundary_files/$folder_name/$year
        done 
    fi 
done 

for folder_name in "${in_detected_fires[@]}"
do 
    mkdir zipped_files/detected_fires/$folder_name
    mkdir unzipped_files/detected_fires/$folder_name

    for year in "${fire_tbl_years[@]}"
    do 
        mkdir unzipped_files/detected_fires/$folder_name/$year
    done 
done 


