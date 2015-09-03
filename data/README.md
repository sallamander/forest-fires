## Data Structure

The data used for this project is all publicly available. At this point, I am using three subgroups of data: 

1.) [Fire detection data](http://firemapper.sc.egov.usda.gov/gisdata.php)  
2.) [State, County, Region, and Urban Area shapfiles](https://www.census.gov/geo/maps-data/data/tiger-cart-boundary.html)  
3.) [Fire perimeter Boundaries](http://rmgsc.cr.usgs.gov/outgoing/GeoMAC/historic_fire_data/)  

All of the zipped files that I have downloaded to use (namely 2013, 2014) are in the zipped_files folder
in this data subdirectory. Data from (1) above are in the /zipped_files/deteced_fires subdirectory, and data from (2) above are located in the /zipped_files/boundary_files subdirectory. 

#### What to follow along, work through my project, or try to add to it?

If you'd like, the unzip.py file in this data subdirectory hsa been built in such a way that it will 
cycle through all of the zipped files in the zipped_files folder, unzip those files, and then move them to an analagous folder in an unzipped_files folder in this data subdirectory (it will also create the unzipped_files folder structure if necessary). After running this, you can hop over to the code subdirectory, navigate to the data_work folder, and follow the README.md there. 