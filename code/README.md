## The Code

The vast majority of the code written for this project is stored in one of the subdirectories found within this `code` directory. To date, there are no files that contain substantial or important pieces of code that are not within one of these subdirectories.    

## Code Structure

A number of these are fairly explanatory (and I've tried to segment the code logically), but in any case, the intended purpose of the code in each of these is as follows: 

* `app` - This contains code for a Flask app that will describe the project. It'll walk through the project in (probably) minimal detail from start to finish, and allow for interaction with the raw data as well as the predictions from any models. It's currently a work in progress, and isn't too far along. 
* `data_setup` - This contains code used to set up the data. Whether that be setup during the ETL phase of the project (before any EDA or modeling starts), or setup in terms of generating data files for the Flask app in the `app` folder, all code for data file and folder setup/creation/generation is contained in this folder. 
* `eda-viz` - This contains a large amount of code using during the exploratory data analysis (EDA) phase of my project, but also other pieces of code used at other points in time. For example, it also contains code used to originally scope the project and determine what the end goal would be (e.g. what would the data actually allow me to do), as well as code used to visualize the results/predictions of any models and examine how they were performing. It also might contain some code use for one-off visualizations for presentations and the like. For the most part, this folder contains IPython notebooks, since they are incredibly nice to use for visualization. 
* `feature_engineering` - This contains all the code used to move from the raw data CSV (output from Postgres) to the Pandas Dataframe/Numpy arrays (or any other format) that can be inputted into the models. This includes any code used to generate new features, transform already existent features, dummify features, etc.
* `makefiles` - This contains code and data files necessary to run the models using `make`. This code isn't strictly necessary, but I wanted to build up the project having `make` accessible (for various reasons), and the code/data files in this folder help to achieve that. For the most part, they are used to control what years of data get moved when/where, what features are created/modified in what way during feature engineering, and what features are included in the final models. 
* `modeling` - This contains code for running models. It's the culmination of the majority of all the code included in other folders. 




