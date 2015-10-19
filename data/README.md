## The Data

The data used for this project is all publicly available. At this point, I am using three subgroups of data: 

1.) [Fire detection data](http://firemapper.sc.egov.usda.gov/gisdata.php)  
2.) [State, County, Region, and Urban Area shapfiles](https://www.census.gov/geo/maps-data/data/tiger-cart-boundary.html)  
3.) [Fire perimeter Boundaries](http://rmgsc.cr.usgs.gov/outgoing/GeoMAC/historic_fire_data/)  

### Data Structure

1.) Each row of the fire detection data is a 'detected fire', as determined by running satellite imagery from NASA’s AUQA and TERRA satellites through [the University of Maryland's active fire detection product](http://modis-fire.umd.edu/pages/ActiveFire.php). For each row, the geometry we have for it is the latitude/longitude. We then also have a number of other observables and outputs from UMD's active fire detection product. 

2.) The state, county, region, and urban area shapefiles contain the boundaries for each of those respective geographic types. As of right now, the census has these files for 1990, 2000, 2010, 2013, and 2014. I'm currently looking at only 2012-2015 data, and will be using the 2014 geographic boundary shapefiles for 2015, and 2013 geographic boundary shapefiles for 2012. 
      
3.) Each state is required to report forest fire perimeter boundaries each day, which is what the fire perimeter boundary files contain. They also contain other information relating to those fires, such as fire name, the date, the number of acres burned thus far, etc. At this point, I am simply using these fire perimeter boundaries to determine if the latitude/longitude coordinates of a detected fire (from data source (1)) fall within a fire perimeter. If they do, 
then I know this detected fire is a forest fire, and otherwise it is not. 

### Want to follow along, add to my work, or improve on it?

If you fork my repo, and then navigate to the data folder, you can run the command 'make data',  and the data file structure will be created for you with the data downloaded and placed into the file structure (this assumes you're running it from a unix terminal).

In essence, what this will do is create a zipped_files folder structure and equivalent unzipped_files folder structure within this data subdirectory, download zipped versions of the data and place those in the zipped_files folder structure, and then unzip those files and place unzipped versions in the unzipped_files folder structure. 
