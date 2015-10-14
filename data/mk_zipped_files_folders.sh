#!/bin/bash

mkdir zipped_files 

in_zipped_files=( boundary_files detected_fires )
in_boundary_files=( county fire_perimeters region state urban_areas )
in_detected_fires=( MODIS )

for folder_name in "${in_zipped_files[@]}"
do 
    mkdir zipped_files/$folder_name
done 

for folder_name in "${in_boundary_files[@]}"
do 
    mkdir zipped_files/boundary_files/$folder_name
done 

for folder_name in "${in_detected_fires[@]}"
do 
    mkdir zipped_files/detected_fires/$folder_name
done 


