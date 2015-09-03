## The Data

The data used for this project is all publicly available. At this point, I am using three subgroups of data: 

1.) [Fire detection data](http://firemapper.sc.egov.usda.gov/gisdata.php)  
2.) [State, County, Region, and Urban Area shapfiles](https://www.census.gov/geo/maps-data/data/tiger-cart-boundary.html)  
3.) [Fire perimeter Boundaries](http://rmgsc.cr.usgs.gov/outgoing/GeoMAC/historic_fire_data/)  

All of the zipped files that I have downloaded to use (namely 2013, 2014) are in the zipped_files folder
in this data subdirectory. Data from (1) above are in the /zipped_files/deteced_fires/ subdirectory, and data from (2) and (3) above are located in the /zipped_files/boundary_files/ subdirectory. 

### Data Structure

1.) Each row of the fire detection data is a 'detected fire' (I say that because not every row is actually a fire), as determined by running satellite imagery from NASA’s AUQA and TERRA satellites through [the University of Maryland's active fire detection product](http://modis-fire.umd.edu/pages/ActiveFire.php). For each row, the geometry we have for it is the latitude/longitude. We then also have a number of other observables and outputs from UMD's active fire detection product. 

2.) The state, county, region, and urban area shapefiles contain the boundaries for each of those respective geographic types. As of right now, the census has these files for 1990, 2000, 2010, 2013, and 2014. I'm currently looking at only 2013-2015 data, and will be using the 2014 geographic boundary shapefiles for 2015.   
3.) Each state is required to report fire perimeter boundaries eacy day, which is what the fire perimeter boundary file contains. It also contains other information relating to those fires, such as fire name, the date, the number of acres burned thus far, etc. 

#### What to follow along, work through my project, or try to add to it?

If you'd like, the unzip.py file in this data subdirectory has been built in such a way that it will 
cycle through all of the zipped files in the zipped_files folder, unzip those files, and then move them to an analagous folder in an unzipped_files folder in this data subdirectory (it will also create the unzipped_files folder structure if necessary). After running this, you can hop over to the code subdirectory, navigate to the data_work folder, and follow the section of the README.md there that has this same section title. 