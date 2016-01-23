.data_folder_structure_sentinel: 
	bash data/mk_folders.sh
	touch .data_folder_structure_sentinel

zipped_folder=data/zipped_files/
unzipped_folder=data/unzipped_files/

county_2013=boundary_files/county/2013
county_2014=boundary_files/county/2014

state_2013=boundary_files/state/2013
state_2014=boundary_files/state/2014

urban_areas_2013=boundary_files/urban_areas/2013
urban_areas_2014=boundary_files/urban_areas/2014

region_2013=boundary_files/region/2013
region_2014=boundary_files/region/2014

fire_perimeters_2012=boundary_files/fire_perimeters/2012
fire_perimeters_2013=boundary_files/fire_perimeters/2013
fire_perimeters_2014=boundary_files/fire_perimeters/2014
fire_perimeters_2015=boundary_files/fire_perimeters/2015

detected_fires_2012=detected_fires/MODIS/2012
detected_fires_2013=detected_fires/MODIS/2013
detected_fires_2014=detected_fires/MODIS/2014
detected_fires_2015=detected_fires/MODIS/2015

$(zipped_folder)$(county_2013).zip: 
	curl http://www2.census.gov/geo/tiger/GENZ2013/cb_2013_us_county_500k.zip \
		-o $(zipped_folder)$(county_2013).zip

	cp $(zipped_folder)$(county_2013).zip $(unzipped_folder)$(county_2013)/

	unzip $(unzipped_folder)$(county_2013)/2013.zip -d $(unzipped_folder)$(county_2013)/

	rm $(unzipped_folder)$(county_2013)/*.zip

$(zipped_folder)$(county_2014).zip:
	curl http://www2.census.gov/geo/tiger/GENZ2014/shp/cb_2014_us_county_500k.zip \
		-o $(zipped_folder)$(county_2014).zip

	cp $(zipped_folder)$(county_2014).zip $(unzipped_folder)$(county_2014)/

	unzip $(unzipped_folder)$(county_2014)/2014.zip -d $(unzipped_folder)$(county_2014)/

	rm $(unzipped_folder)$(county_2014)/*.zip

county_boundaries: $(zipped_folder)$(county_2013).zip $(zipped_folder)$(county_2014).zip

$(zipped_folder)$(state_2013).zip:
	curl http://www2.census.gov/geo/tiger/GENZ2013/cb_2013_us_state_500k.zip \
		-o $(zipped_folder)$(state_2013).zip

	cp $(zipped_folder)$(state_2013).zip $(unzipped_folder)$(state_2013)/

	unzip $(unzipped_folder)$(state_2013)/2013.zip -d $(unzipped_folder)$(state_2013)/

	rm $(unzipped_folder)$(state_2013)/*.zip

$(zipped_folder)$(state_2014).zip:
	curl http://www2.census.gov/geo/tiger/GENZ2014/shp/cb_2014_us_state_500k.zip -o \
		$(zipped_folder)$(state_2014).zip

	cp $(zipped_folder)$(state_2014).zip $(unzipped_folder)$(state_2014)/

	unzip $(unzipped_folder)$(state_2014)/2014.zip -d $(unzipped_folder)$(state_2014)/

	rm $(unzipped_folder)$(state_2014)/*.zip

state_boundaries: $(zipped_folder)$(state_2013).zip $(zipped_folder)$(state_2014).zip 

$(zipped_folder)$(region_2013).zip:
	curl http://www2.census.gov/geo/tiger/GENZ2013/cb_2013_us_region_500k.zip \
		-o $(zipped_folder)$(region_2013).zip

	cp $(zipped_folder)$(region_2013).zip $(unzipped_folder)$(region_2013)/

	unzip $(unzipped_folder)$(region_2013)/2013.zip -d $(unzipped_folder)$(region_2013)/

	rm $(unzipped_folder)$(region_2013)/*.zip

$(zipped_folder)$(region_2014).zip:
	curl http://www2.census.gov/geo/tiger/GENZ2014/shp/cb_2014_us_region_500k.zip \
		-o $(zipped_folder)$(region_2014).zip

	cp $(zipped_folder)$(region_2014).zip $(unzipped_folder)$(region_2014)/

	unzip $(unzipped_folder)$(region_2014)/2014.zip -d $(unzipped_folder)$(region_2014)/

	rm $(unzipped_folder)$(region_2014)/*.zip

region_boundaries: $(zipped_folder)$(region_2013).zip $(zipped_folder)$(region_2014).zip

$(zipped_folder)$(urban_areas_2013).zip:
	curl http://www2.census.gov/geo/tiger/GENZ2013/cb_2013_us_ua10_500k.zip \
		-o $(zipped_folder)$(urban_areas_2013).zip

	cp $(zipped_folder)$(urban_areas_2013).zip $(unzipped_folder)$(urban_areas_2013)/

	unzip $(unzipped_folder)$(urban_areas_2013)/2013.zip \
		-d $(unzipped_folder)$(urban_areas_2013)/

	rm $(unzipped_folder)$(urban_areas_2013)/*.zip

$(zipped_folder)$(urban_areas_2014).zip:
	curl http://www2.census.gov/geo/tiger/GENZ2014/shp/cb_2014_us_ua10_500k.zip \
		-o $(zipped_folder)$(urban_areas_2014).zip

	cp $(zipped_folder)$(urban_areas_2014).zip $(unzipped_folder)$(urban_areas_2014)/

	unzip $(unzipped_folder)$(urban_areas_2014)/2014.zip \
		-d $(unzipped_folder)$(urban_areas_2014)/

	rm $(unzipped_folder)$(urban_areas_2014)/*.zip

urban_area_boundaries: $(zipped_folder)$(urban_areas_2013).zip \
						$(zipped_folder)$(urban_areas_2014).zip

$(zipped_folder)$(fire_perimeters_2012).zip: 
	curl http://rmgsc.cr.usgs.gov/outgoing/GeoMAC/historic_fire_data/2012_perimeters_dd83.zip \
		-o $(zipped_folder)$(fire_perimeters_2012).zip

	cp $(zipped_folder)$(fire_perimeters_2012).zip $(unzipped_folder)$(fire_perimeters_2012)/

	unzip $(unzipped_folder)$(fire_perimeters_2012)/2012.zip \
		-d $(unzipped_folder)$(fire_perimeters_2012)/

	rm $(unzipped_folder)$(fire_perimeters_2012)/*.zip

$(zipped_folder)$(fire_perimeters_2013).zip: 
	curl http://rmgsc.cr.usgs.gov/outgoing/GeoMAC/historic_fire_data/2013_perimeters_dd83.zip \
		-o $(zipped_folder)$(fire_perimeters_2013).zip

	cp $(zipped_folder)$(fire_perimeters_2013).zip $(unzipped_folder)$(fire_perimeters_2013)/

	unzip $(unzipped_folder)$(fire_perimeters_2013)/2013.zip \
		-d $(unzipped_folder)$(fire_perimeters_2013)/

	rm $(unzipped_folder)$(fire_perimeters_2013)/*.zip

$(zipped_folder)$(fire_perimeters_2014).zip: 
	curl http://rmgsc.cr.usgs.gov/outgoing/GeoMAC/historic_fire_data/2014_perimeters_dd83.zip \
		-o $(zipped_folder)$(fire_perimeters_2014).zip

	cp $(zipped_folder)$(fire_perimeters_2014).zip $(unzipped_folder)$(fire_perimeters_2014)/

	unzip $(unzipped_folder)$(fire_perimeters_2014)/2014.zip \
		-d $(unzipped_folder)$(fire_perimeters_2014)/

	rm $(unzipped_folder)$(fire_perimeters_2014)/*.zip

$(zipped_folder)$(fire_perimeters_2015).zip: 
	curl http://rmgsc.cr.usgs.gov/outgoing/GeoMAC/historic_fire_data/2015_perimeters_dd83.zip \
		-o $(zipped_folder)$(fire_perimeters_2015).zip

	cp $(zipped_folder)$(fire_perimeters_2015).zip $(unzipped_folder)$(fire_perimeters_2015)/

	unzip $(unzipped_folder)$(fire_perimeters_2015)/2015.zip \
		-d $(unzipped_folder)$(fire_perimeters_2015)/

	rm $(unzipped_folder)$(fire_perimeters_2015)/*.zip

fire_perimeter_boundaries: $(zipped_folder)$(fire_perimeters_2012).zip \
							$(zipped_folder)$(fire_perimeters_2013).zip \
							$(zipped_folder)$(fire_perimeters_2014).zip \
							$(zipped_folder)$(fire_perimeters_2015).zip

$(zipped_folder)$(detected_fires_2012).zip: 
	curl http://activefiremaps.fs.fed.us/data/fireptdata/modis_fire_2012_366_conus_shapefile.zip \
		-o $(zipped_folder)$(detected_fires_2012).zip

	cp $(zipped_folder)$(detected_fires_2012).zip $(unzipped_folder)$(detected_fires_2012)/

	unzip $(unzipped_folder)$(detected_fires_2012)/2012.zip \
		-d $(unzipped_folder)$(detected_fires_2012)/

	rm $(unzipped_folder)$(detected_fires_2012)/*.zip

$(zipped_folder)$(detected_fires_2013).zip: 
	curl http://activefiremaps.fs.fed.us/data/fireptdata/modis_fire_2013_365_conus_shapefile.zip \
		-o $(zipped_folder)$(detected_fires_2013).zip

	cp $(zipped_folder)$(detected_fires_2013).zip $(unzipped_folder)$(detected_fires_2013)/

	unzip $(unzipped_folder)$(detected_fires_2013)/2013.zip \
		-d $(unzipped_folder)$(detected_fires_2013)/

	rm $(unzipped_folder)$(detected_fires_2013)/*.zip

$(zipped_folder)$(detected_fires_2014).zip: 
	curl http://activefiremaps.fs.fed.us/data/fireptdata/modis_fire_2014_365_conus_shapefile.zip \
		-o $(zipped_folder)$(detected_fires_2014).zip

	cp $(zipped_folder)$(detected_fires_2014).zip $(unzipped_folder)$(detected_fires_2014)/

	unzip $(unzipped_folder)$(detected_fires_2014)/2014.zip \
		-d $(unzipped_folder)$(detected_fires_2014)/

	rm $(unzipped_folder)$(detected_fires_2014)/*.zip

$(zipped_folder)$(detected_fires_2015).zip: 
	curl http://activefiremaps.fs.fed.us/data/fireptdata/modis_fire_2015_365_conus_shapefile.zip \
		-o $(zipped_folder)$(detected_fires_2015).zip

	cp $(zipped_folder)$(detected_fires_2015).zip $(unzipped_folder)$(detected_fires_2015)/

	unzip $(unzipped_folder)$(detected_fires_2015)/2015.zip \
		-d $(unzipped_folder)$(detected_fires_2015)/

	rm $(unzipped_folder)$(detected_fires_2015)/*.zip

detected_fires: $(zipped_folder)$(detected_fires_2012).zip \
				$(zipped_folder)$(detected_fires_2013).zip \
				$(zipped_folder)$(detected_fires_2014).zip \
				$(zipped_folder)$(detected_fires_2015).zip

get_data: .data_folder_structure_sentinel county_boundaries state_boundaries region_boundaries \
			 urban_area_boundaries fire_perimeter_boundaries detected_fires 

.data_prep_sentinel: 
	bash code/data_setup/manage_psql_dts.sh -c
	bash code/data_setup/manage_psql_dts.sh -r

	bash code/data_setup/manage_psql_dts.sh -m fire 2012 
	bash code/data_setup/manage_psql_dts.sh -m fire 2013
	bash code/data_setup/manage_psql_dts.sh -m fire 2014 
	bash code/data_setup/manage_psql_dts.sh -m fire 2015 

	bash code/data_setup/manage_psql_dts.sh -m urban_areas 2012 
	bash code/data_setup/manage_psql_dts.sh -m urban_areas 2013 
	bash code/data_setup/manage_psql_dts.sh -m urban_areas 2014 
	bash code/data_setup/manage_psql_dts.sh -m urban_areas 2015

	bash code/data_setup/manage_psql_dts.sh -m region 2012  
	bash code/data_setup/manage_psql_dts.sh -m region 2013
	bash code/data_setup/manage_psql_dts.sh -m region 2014  
	bash code/data_setup/manage_psql_dts.sh -m region 2015

	bash code/data_setup/manage_psql_dts.sh -m county 2012   
	bash code/data_setup/manage_psql_dts.sh -m county 2013   
	bash code/data_setup/manage_psql_dts.sh -m county 2014   
	bash code/data_setup/manage_psql_dts.sh -m county 2015

	bash code/data_setup/manage_psql_dts.sh -m state 2012    
	bash code/data_setup/manage_psql_dts.sh -m state 2013    
	bash code/data_setup/manage_psql_dts.sh -m state 2014    
	bash code/data_setup/manage_psql_dts.sh -m state 2015   

	bash code/data_setup/manage_psql_dts.sh -o 

	touch .data_prep_sentinel

prep_data: .data_prep_sentinel

data: get_data prep_data

.features_sentinel: code/makefiles/time_transforms_dict.pkl \
	code/makefiles/time_transforms_dict.pkl code/makefiles/year_list.pkl \
	
	if [ ! -d code/modeling/model_input ]; then \
		mkdir code/modeling/model_input; \
		chmod 777 code/modeling/model_input; \
	fi 
	python code/feature_engineering/create_inputs.py geo time
	touch .features_sentinel

features: .features_sentinel

models: .models_sentinel
	if [ ! -d code/modeling/model_output ]; then \
			mkdir -p code/modeling/model_output/logs; \
			chmod 777 code/modeling/model_output/logs; \
	fi 

	bash code/modeling/run_models.sh

.models_sentinel: 
	touch .models_sentinel

