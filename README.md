# forest-fires

With the right compilation of datasets, can we build a machine learning model for the early detection of forest fires?
Furthermore, can we extend that early detection model to predict ahead of time how severe a forest fire will be?

Using the [fire detection data set from the National Forest Services](http://firemapper.sc.egov.usda.gov/gisdata.php),
I aim to predict whether each 'detected fire' is (a.) An actual fire, and (b.) Whether or not those fires which are 
actual fires are forest fires. To do so, I plan to train a model using [historical forest fire perimeter boundaries]
(http://rmgsc.cr.usgs.gov/outgoing/GeoMAC/historic_fire_data/) as the target variable/ground truth. That is, if a 
detected fire falls within a forest fire perimeter boundary for the given date that it occurs, I will consider it 
a forest fire and use that as my ground truth. 
