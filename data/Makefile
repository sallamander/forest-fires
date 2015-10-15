zipped_files: 
	sh mk_zipped_files_folders.sh 

county_2013=zipped_files/boundary_files/county/2013.zip
county_2014=zipped_files/boundary_files/county/2014.zip

state_2013=zipped_files/boundary_files/state/2013.zip
state_2014=zipped_files/boundary_files/state/2014.zip

urban_areas_2013=zipped_files/boundary_files/urban_areas/2013.zip
urban_areas_2014=zipped_files/boundary_files/urban_areas/2014.zip

region_2013=zipped_files/boundary_files/region/2013.zip
region_2014=zipped_files/boundary_files/region/2014.zip

fire_perimeters_2012=zipped_files/boundary_files/fire_perimeters/2012.zip
fire_perimeters_2013=zipped_files/boundary_files/fire_perimeters/2013.zip
fire_perimeters_2014=zipped_files/boundary_files/fire_perimeters/2014.zip
fire_perimeters_2015=zipped_files/boundary_files/fire_perimeters/2015.zip

detected_fires_2012=zipped_files/detected_fires/MODIS/2012.zip
detected_fires_2013=zipped_files/detected_fires/MODIS/2013.zip
detected_fires_2014=zipped_files/detected_fires/MODIS/2014.zip
detected_fires_2015=zipped_files/detected_fires/MODIS/2015.zip

$(county_2013): 
	curl http://www2.census.gov/geo/tiger/GENZ2013/cb_2013_us_county_500k.zip \
		-o $(county_2013)

$(county_2014):
	curl http://www2.census.gov/geo/tiger/GENZ2014/shp/cb_2014_us_county_500k.zip \
		-o $(county_2014)

county_boundaries: $(county_2013) $(county_2014) 

$(state_2013):
	curl http://www2.census.gov/geo/tiger/GENZ2013/cb_2013_us_state_500k.zip \
		-o $(state_2013) 

$(state_2014):
	curl http://www2.census.gov/geo/tiger/GENZ2014/shp/cb_2014_us_state_500k.zip -o $(state_2014) 

state_boundaries: $(state_2013) $(state_2014) zipped_files

$(region_2013):
	curl http://www2.census.gov/geo/tiger/GENZ2013/cb_2013_us_region_500k.zip \
		-o $(region_2013)

$(region_2014):
	curl http://www2.census.gov/geo/tiger/GENZ2014/shp/cb_2014_us_region_500k.zip \
		-o $(region_2014)

region_boundaries: $(region_2013) $(region_2014) zipped_files

$(urban_areas_2013):
	curl http://www2.census.gov/geo/tiger/GENZ2013/cb_2013_us_ua10_500k.zip \
		-o $(urban_areas_2013) 

$(urban_areas_2014):
	curl http://www2.census.gov/geo/tiger/GENZ2014/shp/cb_2014_us_ua10_500k.zip \
		-o $(urban_areas_2014)

urban_area_boundaries: $(urban_areas_2013) $(urban_areas_2014)

$(fire_perimeters_2012): 
	curl http://rmgsc.cr.usgs.gov/outgoing/GeoMAC/historic_fire_data/2012_perimeters_dd83.zip \
		-o $(fire_perimeters_2012)

$(fire_perimeters_2013): 
	curl http://rmgsc.cr.usgs.gov/outgoing/GeoMAC/historic_fire_data/2013_perimeters_dd83.zip \
		-o $(fire_perimeters_2013)

$(fire_perimeters_2014): 
	curl http://rmgsc.cr.usgs.gov/outgoing/GeoMAC/historic_fire_data/2014_perimeters_dd83.zip \
		-o $(fire_perimeters_2014)

$(fire_perimeters_2015): 
	curl http://rmgsc.cr.usgs.gov/outgoing/GeoMAC/current_year_fire_data/current_year_all_states/perimeters_dd83.zip \
		-o $(fire_perimeters_2015)

fire_perimeter_boundaries: $(fire_perimeters_2012) $(fire_perimeters_2013) \
							$(fire_perimeters_2014) $(fire_perimeters_2015)

$(detected_fires_2012): 
	curl http://activefiremaps.fs.fed.us/data/fireptdata/modis_fire_2012_366_conus_shapefile.zip \
		-o $(detected_fires_2012)

$(detected_fires_2013): 
	curl http://activefiremaps.fs.fed.us/data/fireptdata/modis_fire_2013_366_conus_shapefile.zip \
		-o $(detected_fires_2013)

$(detected_fires_2014): 
	curl http://activefiremaps.fs.fed.us/data/fireptdata/modis_fire_2014_366_conus_shapefile.zip \
		-o $(detected_fires_2014)

$(detected_fires_2015): 
	curl http://activefiremaps.fs.fed.us/data/fireptdata/modis_fire_2014_366_conus_shapefile.zip \
		-o $(detected_fires_2015)

detected_fires: $(detected_fires_2012) $(detected_fires_2013) \
					$(detected_fires_2014) $(detected_fires_2015)

zipped_data: zipped_files county_boundaries state_boundaries region_boundaries urban_area_boundaries fire_perimeter_boundaries detected_fires 


