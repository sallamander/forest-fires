#!/bin/bash

mkdir zipped_files 
mkdir unzipped_files 

in_zip_unzip_files=( boundary_files detected_fires )
in_boundary_files=( county fire_perimeters region state urban_areas )
in_detected_fires=( MODIS )

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
        mkdir unzipped_files/boundary_files/$folder_name/2012
        mkdir unzipped_files/boundary_files/$folder_name/2013
        mkdir unzipped_files/boundary_files/$folder_name/2014
        mkdir unzipped_files/boundary_files/$folder_name/2015 
    else 
        mkdir unzipped_files/boundary_files/$folder_name/2013
        mkdir unzipped_files/boundary_files/$folder_name/2014
    fi 
done 

for folder_name in "${in_detected_fires[@]}"
do 
    mkdir zipped_files/detected_fires/$folder_name
    mkdir unzipped_files/detected_fires/$folder_name
    mkdir unzipped_files/detected_fires/$folder_name/2012
    mkdir unzipped_files/detected_fires/$folder_name/2013
    mkdir unzipped_files/detected_fires/$folder_name/2014
    mkdir unzipped_files/detected_fires/$folder_name/2015 
done 


