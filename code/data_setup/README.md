## Folder Workflow 

`manage_psql_dts.sh` is called a number of times during the running of `make data` from the main folder of this repository. The workflow of that `make data` command and how it uses this `manage_psql_dts.sh` goes something like this:  

1.) **Read all data into a Postgres table**. While a Postgres table may be a little heavy to use for the size of data in this project, there is a postgres GIS extension that makes it incredibly easy to read in shapefiles, and then perform geometry calculations between different shapes (intersections, for example). For this reason, it is stored in Postgres until any/all geometry calculations are done. 

2.) **Perform any/all geometry calculations**. As of right now, this means taking each fire centroid location (i.e. lat/long coordinate), and figuring out what state/county/region boundary it is in, whether or not it is in an urban area boundary, and whether or not it falls within a given distance of a forest fire perimeter boundary (if it does, it's labeled as a forest fire) within a given time period. 

3.) **Output the relevant Postgres tables to a more lightweight storage format (CSV)**. For now, the only relevant Postgres table I will be taking is the fire detection data with columns for all of the geometry calculations performed above.


