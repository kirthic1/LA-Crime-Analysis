[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/q4BQ8R99)
# DSCI 510 Final Project

## Name of the Project
Deep Analysis of Crime in Los Angeles
## Team Members (Name and Student IDs)
Kirthi Chillakanti 
Student ID: 8900-2352-76
Email: kchillak@usc.edu

## Raw Data Files over 100MB
crime_data.json - https://drive.google.com/file/d/1Mn2GfznyOwsKebYN6tAxPME1SNEgJJfk/view?usp=drive_link

## Processed Data Files over 100MB
crime_data_processed.json - https://drive.google.com/file/d/1klXS8BBNg6o6Qj5aOrCLJTgCtstAQcIN/view?usp=drive_link
combined_crime_csa_data_processed.geojson - https://drive.google.com/file/d/1Umi2ap5M5QhIFAWypI35UyTecrGHRM9r/view?usp=drive_link
combined_crime_districts_data_processed.geojson - https://drive.google.com/file/d/1QeCeODReMFBmCtpPhgY7kfc2Zp35D8_G/view?usp=drive_link
combined_crime_spa_data_processed.geojson - https://drive.google.com/file/d/1o5aQZW3lSMlRnNXklZtIHDpFDfX8A9os/view?usp=drive_link

## Instructions to create a conda enviornment
1. Install Conda 
2. conda create -n name_of_env python=3.12.4 
3. conda activate name_of_env

## Instructions on how to install the required libraries
1. Ensure steps 1-3 in "Instructions to create a conda environment" are done
2. Clone the git repository. git clone git@github.com:USC-DSCI-510/final-project24-kirthi-final-project.git (Ensure 
   you have SSH key before cloning) 
3. Change directory (cd in Terminal) to the cloned git repository folder
4. pip install -r requirements.txt

## Instructions on how to download the data
The following provides information on how the code in get_data.py retrieved each dataset. 
Hence, for the user's convenience, to retrieve the data, user should simply run the get_data.py code. 
The below is supplementary information on how the code in get_data.py works, and how the data was collected. 
User should not follow the below, as get_data.py will do it for the user.
In order to independently view the data, follow the below steps. 

Crime Data from API
1. Go to https://data.lacity.org/Public-Safety/Crime-Data-from-2020-to-Present/2nrs-mtv8/about_data
2. Click on Export, API Endpoint, API documentation
3. Sign up for App token
4. Use the App token in request to API
5. Use offset and limit parameters to retrieve data in small sets

Poverty Data from API
1. Go to https://geohub.lacity.org/datasets/lacounty::below-poverty-census-tract/about
2. Click on View API Resources
3. Copy the link in GeoService, and truncate it to "query"
4. Use this link url in the request to API, specifying parameter values,
"where": "1=1", "outFields": "*", "f": "geojson", "resultRecordCount": 2000, "outSR": 2229 

Unemployment Data from API
1. Go to https://geohub.lacity.org/datasets/lacounty::unemployment-census-tract/about
2. Click on View API Resources
3. Copy the link in GeoService, and truncate it to "query"
4. Use this link url in the request to API, specifying parameter values,
"where": "1=1", "outFields": "*", "f": "geojson", "resultRecordCount": 2000, "outSR": 2229

District Data from API
1. Go to https://geohub.lacity.org/datasets/lacounty::supervisorial-districts-current/about
2. Click on View API Resources
3. Copy the link in GeoService, and truncate it to "query"
4. Use this link url in the request to API, specifying parameter values,
"where": "1=1",  "outFields": "*", "f": "geojson", "outSR": 2229

Service Planning Areas (SPA) Data from API
1. Go to https://geohub.lacity.org/datasets/lacounty::la-county-service-planning-area-2012/about
2. Click on View API Resources
3. Copy the link in GeoService, and truncate it to "query"
4. Use this link url in the request to API, specifying parameter values,
"where": "1=1",  "outFields": "*", "f": "geojson", "outSR": 2229

Countywide Statistical Areas(CSA) Data from API
1. Go to https://geohub.lacity.org/datasets/lacounty::countywide-statistical-areas-csas/about
2. Click on View API Resources
3. Copy the link in GeoService, and truncate it to "query"
4. Use this link url in the request to API, specifying parameter values,
"where": "1=1",  "outFields": "*", "f": "geojson", "outSR": 2229

## Instructions on how to clean the data
The clean_data.py file in this project contains the code for cleaning the datasets, 
which involves removing duplicates, removing rows with null values, merging datasets, and creating new columns 
in preparation for analysis. 

Input: raw data files in final-project24-kirthi-final-project/data/raw

Expected Output: processed data files in final-project24-kirthi-final-project/data/processed
Prints information on processed dataframes 

1. Ensure "Instructions to create a conda environment" and "Instructions on how to install the required libraries" 
   are done.   
2. Create project in PyCharm or any IDE
3. Ensure that the virtual environment in the IDE is set to the one created 
   in "Instructions to create a conda environment"
4. Move cloned git repository folder to inside the Pycharm/IDE project folder
5. Open the get_data.py file in the IDE you are using
6. Click Run to run the get_data.py file to retrieve all data
7. Open the clean_data.py file in the IDE you are using
8. Click Run to run the clean_data.py file

Additional Notes: 
The get_data.py file and the clean_data.py file will take time to run as it involves large datasets. 

## Instrucions on how to run analysis code
Input: processed data files in final-project24-kirthi-final-project/data/processed

Expected Output: 18 DataFrames

1. Ensure steps 1-8 in "Instructions on how to clean the data" are done.
2. Open the run_analysis.py file in the IDE you are using
3. Click Run

Additional Notes: 
The run_analysis.py file will take time to run as it involves large datasets. 

## Instructions on how to create visualizations
Input: processed data files in final-project24-kirthi-final-project/data/processed

Expected Output: Combination of bar charts, scatterplots, and maps

1. Ensure steps 1-3 in "Instructions on how to run analysis code" are done. 

Registering the newly created and active virtual environment with jupyterlab
1. Ensure ipykernel is installed in virtual environment. If not, do conda install ipykernel
2. Ensure jupyter lab/jupyter notebook is installed in virtual environment. If not, do conda install jupyterlab
3. Register your conda environment with jupyter by running: 
python -m ipykernel install --name name_of_env --display-name name_of_env --user


Running visualize_results.ipynb in jupyter lab directly
1. Open jupyter lab by giving the following command in terminal: jupyter lab 
2. Navigate to repository folder where the visualize_results.ipynb file is in
3. Click and open the file. 
4. Ensure that the virtual environment in jupyter lab is set to the one created in "Instructions to create a conda environment" 
5. Click Run

Running visualize_results.ipynb in Pycharm/IDE
1. Open the visualize_results.ipynb file in the IDE you are using
2. Click Run

Additional Notes: 
The visualize_results.ipynb file will take time to run as it involves large datasets. 
