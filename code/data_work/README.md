## Folder Workflow 

The workflow for this folder goes something like this: 

1.) Read all data into a Postgres table. While I know that a Postgres table may be a little heavy to use for the size of my data, there is a postgres GIS extension that makes it incredibly easy to read in shapefiles, and then perform geometry calculations between different shapes (intersections, for example). For this reason, I will be storing my data in Postgres until I am done with any/all gemoetry calcuations. 

2.) Perform any/all gemoetry calculations. As of right now, this means taking each fire centroid location (i.e. lat/long coordinate), and figuring out what state/county/region boundary it is in, whether or not it is in an urban area boundary, and whether or not it falls within a forest fire perimeter boundary (if it does, I'm labeling it as a forest fire). 

3.) Output the relevant Postgres tables to a more lightweight storage format (probably CSV, or CSV to a pickled pandas dataframe). For now, the only relevant Postgres table I will be taking is the fire detection data with columns for all of the geometry calculations performed above.

4.) Other steps forthcoming...

#### Want to follow along, work through my project, or try to add to it?

At this point in time (and I will keep this README.md up-to-date), the only python file that is relevant is the create_postgres_dts.py file. Running that will read in all of the data for whatever year(s) you put in (note that it requires a pickled list file as input) - the detected fires and all boundary shapefiles (state, county, region, urban area, and forest fire perimeter). 

To run the create_postgres_dts.py file, it will take a little bit of setup. First off, you'll have to have Postgres installed. I'm not going to get into the best way to do this because it depends on the machine your operating on and of the hundreds of blog posts describing how to do it, I'm not gaurenteed to pick the one that will hit home with every person reading this. Let's assume you have it installed, **and** that you have a Postgres instance up and running...

The next step is that you need to create the forest_fires database on your machine, and add the GIS extension. Provided you have Postgres up and running, you can type in the following commands. Note that psql is my unix alias for opening postgres, so you might have to type something slightly different if your alias is not the same.  Also note that I have configured my settings in such a way that I do not need to type in any kind of username/password to get into Postgres. 

```unix 
psql # Open Postgres. 
psql CREATE DATABASE forest_fires; # Create the forest fires database. 

\q # Exit back to the terminal so you can log into the forest_fires database. 

psql forest_fires; # Log into the forest_fires database. 
CREATE EXTENSION POSTGIS; # Add the POSTGIS extension to the forest_fires database. 
```

After this step, feel free to log out of the forest_fires database (or stay logged in so you can verify the results of the create_postgres_dts.py file), **but** don't stop running Postgres on your machine.   

You are now ready to run the create_postgres_dts.py file and have all of the datatables created in your forest_fires database. I'm going to spare you the details of creating the pickled list that I'm using as input into the create_postgres_dts.py (I did it this way so I could make use of a Makefile), but from within the /code/data_work folder you can run it as follows: 

```python 
python create_postgres_dts.py ../../makefiles/year_list.pkl 
```






