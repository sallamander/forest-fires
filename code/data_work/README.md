#### Wnat to follow along, work through my project, or try to add to it?

The workflow for this folder goes something like this: 

1.) Read all data into a Postgres table. While I know that a Postgres table may be a little heavy to use for the size of my data, there is a postgres GIS extension that makes it incredibly easy to read in shapefiles, and then perform geometry calculations between different shapes (intersections, for example). For this reason, I will be storing my data in Postgres until I am done with any/all gemoetry calcuations. 

2.) Perform any/all gemoetry calculations. As of right now