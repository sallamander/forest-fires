## Folder Workflow 

The workflow for this folder goes something like this: 

1.) Read all data into a Postgres table. While I know that a Postgres table may be a little heavy to use for the size of my data, there is a postgres GIS extension that makes it incredibly easy to read in shapefiles, and then perform geometry calculations between different shapes (intersections, for example). For this reason, I will be storing my data in Postgres until I am done with any/all gemoetry calcuations. 

2.) Perform any/all gemoetry calculations. As of right now, this means taking each fire centroid location (i.e. lat/long coordinate), and figuring out what state/county/region boundary it is in, whether or not it is in an urban area boundary, and whether or not it falls within a fire perimeter boundary (if it does, I'm labeling it as a fire). 

3.) Output the relevant Postgres tables to a more lightweight storage format (probably CSV, or CSV to a pickled pandas dataframe). For now, the only relevant Postgres table I will be taking is the fire detection data with columns for all of the geometry calculations performed above.

4.) Other steps forthcoming...



