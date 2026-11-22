import pandas as pd
import geopandas as gpd
import os

processed_data_folder = "../data/processed"


def crime_data_clean() -> pd.DataFrame:
    """
    Data cleaning and processing on CRIME DATA.
    Removes duplicate rows, processes missing values, adds separate columns for year, month, hour, time groups,
    and writes the newly processed/cleaned Los Angeles CRIME data to a JSON file in the data/processed folder.
    :return: pd.DataFrame
    """
    # The dtype{"time_occ":str} ensures that it reads time_occ as string, and does not remove the trailing zeros
    results_df = pd.read_json("../data/raw/crime_data.json", dtype={"time_occ": str})

    # Processing the day/time columns.
    results_df["date_occ"] = pd.to_datetime(results_df["date_occ"])
    results_df["year"] = results_df["date_occ"].dt.year
    results_df["month"] = results_df["date_occ"].dt.month
    results_df["time_occ"] = pd.to_datetime(results_df["time_occ"], format="%H%M")
    results_df["hour"] = results_df["time_occ"].dt.hour
    results_df["Time Groups"] = results_df["hour"].apply(
        lambda x: "Morning" if x < 12 else ("Afternoon" if x < 17 else "Evening")
    )

    # Replacing NA values for mocodes with Unknown.
    # Mocodes define codes for different types of criminal/suspect behaviors
    results_df["mocodes"] = results_df["mocodes"].fillna("Unknown")

    # Replacing NA values for weapon_desc with UNKNOWN WEAPON/OTHER WEAPON,
    # Now, all unknown type of weapon values are consolidated into one cateogry as UNKNOWN WEAPON/OTHER
    # WEAPON
    results_df["weapon_desc"] = results_df["weapon_desc"].fillna("UNKNOWN WEAPON/OTHER WEAPON")

    # Replacing all NA values and unknown values for victim_desc with X.
    results_df["vict_descent"] = results_df["vict_descent"].fillna("X")
    results_df["vict_descent"] = results_df["vict_descent"].replace("-", "X")

    # If victim age less than zero or greater than 100, replacing the value with zero. Zero represents unknown age.
    results_df["vict_age"] = results_df["vict_age"].apply(lambda x: 0 if x < 0 else x)
    results_df["vict_age"] = results_df["vict_age"].apply(lambda x: 0 if x > 100 else x)

    # Replacing all unknown values of victim_sex with X.
    # Assuming "H" means unknown, so replacing "H" with X.
    results_df["vict_sex"] = results_df["vict_sex"].fillna("X")
    results_df["vict_sex"] = results_df["vict_sex"].replace("-", "X")
    results_df["vict_sex"] = results_df["vict_sex"].replace("H", "X")

    # Replacing all NA values of premis_desc with Unknown.
    results_df["premis_desc"] = results_df["premis_desc"].fillna("Unknown")

    # Dropping any duplicate rows.
    results_df.drop_duplicates(keep="first", inplace=True)

    # Writing JSON data to file in data/processed folder.
    results_df = results_df.reset_index(drop=True)
    results_df["date_occ"] = results_df["date_occ"].astype(str)
    results_df["time_occ"] = results_df["time_occ"].astype(str)
    processed_crime_data = os.path.join(processed_data_folder, "crime_data_processed.json")
    results_df.to_json(processed_crime_data, orient="records", lines=False)

    return results_df


def district_data_clean() -> None:
    """
    Data cleaning and processing on DISTRICT DATA.
    No processing/cleaning to be performed on raw geospatial Los Angeles district data. Hence, this function creates
    a GeoJSON file with the same data in the data/processed folder.
    The coordinate reference system is 2229, and hence, the Shape.STArea() column is in sqaure feet.
    :return: None
    """
    gdf_districts = gpd.read_file("../data/raw/district_data.geojson")
    processed_districts = os.path.join(processed_data_folder, "districts_data_processed.geojson")
    gdf_districts.to_file(processed_districts, driver="GeoJSON")


def poverty_data_clean() -> gpd.GeoDataFrame:
    """
    Data cleaning and processing on POVERTY DATA.
    This function processes the raw poverty dataset by handling null values and checking for duplicate rows. This
    function then writes the newly processed/cleaned data to a GeoJSON file in the data/processed folder.
    :return: gpd.GeoDataFrame
    """
    # Reads data from raw poverty data file, and puts into a GeoData Frame.
    gdf_poverty = gpd.read_file("../data/raw/poverty_data.geojson")

    # Drops the rows where the values for "below_fpl_pct" are null.
    # fpl is federal poverty line.
    # "below_fpl_pct" is the percentage of people below the federal poverty line
    below_fpl_pct_is_na = gdf_poverty[gdf_poverty["below_fpl_pct"].isna()]
    gdf_poverty.drop(below_fpl_pct_is_na.index, inplace=True)

    # Drops any rows where the values for "fpl_universe" is zero.
    # "fpl_universe" is the population that is considered when calculating poverty statistics
    fpl_universe_is_zero = gdf_poverty[gdf_poverty["fpl_universe"] == 0]
    gdf_poverty.drop(fpl_universe_is_zero.index, inplace=True)

    # Checks for duplicate rows, and removes them if any.
    duplicates = gdf_poverty[gdf_poverty.duplicated(keep=False)]
    if len(duplicates) > 0:
        gdf_poverty.drop_duplicates(keep="first", inplace=True)

    # Writing processed data to GeoJSON file in the data/prcessed folder.
    processed_poverty = os.path.join(processed_data_folder, "poverty_data_processed.geojson")
    gdf_poverty.to_file(processed_poverty, driver="GeoJSON")

    return gdf_poverty


def combining_crime_and_district_data() -> gpd.GeoDataFrame:
    """
    Combining CRIME and DISTRICT processed datasets, and processing it further.
    This function performs a spatial join between the CRIME dataset and the DISTRICT dataset, and processes this
    combined dataset by handling duplicate rows and unmatched rows. This function then writes this new dataset to a
    GeoJSON file in the data/processed folder. This joined dataset is necessary because the CRIME dataset does not
    contain a district column, and I would like to analyze crime locations at the district level.
    :return: gpd.GeoDataFrame
    """
    # Reads the processed crime dataset and puts it into a pandas dataframe
    results_df = pd.read_json("../data/processed/crime_data_processed.json", dtype={"time_occ": str, "date_occ": str})

    # Converting the crime dataframe into a geodataframe based on the latitude and longitude columns.
    # Setting the coordinate reference system (CRS) to 2229.
    # This is necessary because the datasets in geospatial join need to have the same CRS.
    # This code first sets the CRS to 4326 because this is the standard CRS for longitude and latitude.
    # After setting the CRS to 4326, then the code directs the CRS to 2229, which is the same CRS that the district
    # data is in.
    gdf_crime = gpd.GeoDataFrame(results_df, geometry=gpd.points_from_xy(results_df.lon, results_df.lat))
    gdf_crime.set_crs("EPSG:4326", inplace=True)
    gdf_crime = gdf_crime.to_crs("EPSG:2229")

    # Reading the processed district dataset and putting it into a GeoData Frame.
    # The read_file method preserves the CRS information of data
    gdf_districts = gpd.read_file("../data/processed/districts_data_processed.geojson")

    # Performs spatial join between the now geospatial crime dataset and the geospatial district dataset.
    # The "within" predicate means that if a crime incident location is within a district boundary coordinates,
    # then those two rows are joined together.
    # how = "left" means all the rows from the crime dataset will be in the joined dataset
    gdf_joined_crime_districts = gdf_crime.sjoin(gdf_districts, how="left", predicate="within")

    # Checking for any duplicate rows, and removing them if any.
    duplicates = gdf_joined_crime_districts[gdf_joined_crime_districts.duplicated(keep=False)]
    if len(duplicates) > 0:
        gdf_joined_crime_districts.drop_duplicates(keep="first", inplace=True)

    # Checking for any rows with all null values.
    rows_with_all_na = gdf_joined_crime_districts[gdf_joined_crime_districts.isna().all(axis=1)]
    if len(rows_with_all_na) > 0:
        gdf_joined_crime_districts.drop(rows_with_all_na.index, inplace=True)

    # Checking for unmatched rows which may result when performing joins. Dropping them if any.
    right_columns = ["OBJECTID", "Shape.STArea()", "Shape.STLength()", "DISTRICT", "LABEL"]
    unmatched_rows = gdf_joined_crime_districts[gdf_joined_crime_districts[right_columns].isna().all(axis=1)]
    gdf_joined_crime_districts.drop(unmatched_rows.index, inplace=True)

    # Writing processed data to GeoJSON file in the data/prcessed folder.
    processed_combined_crime_districts = os.path.join(
        processed_data_folder, "combined_crime_districts_data_processed.geojson"
    )
    gdf_joined_crime_districts.to_file(processed_combined_crime_districts, driver="GeoJSON")

    return gdf_joined_crime_districts


def spa_data_clean() -> None:
    """
    Data cleaning and processing on SERVICE PLANNING AREAS (SPA) DATA.
    No processing/cleaning to be performed on raw geospatial Los Angeles SPA data. Hence, this function creates
    a GeoJSON file with the same data in the data/processed folder.
    The coordinate reference system is 2229, and hence, the Shape Area column is in sqaure feet.
    :return: None
    """
    gdf_spa = gpd.read_file("../data/raw/spa_data.geojson")
    processed_spa = os.path.join(processed_data_folder, "spa_data_processed.geojson")
    gdf_spa.to_file(processed_spa, driver="GeoJSON")


def combining_crime_and_spa_data() -> gpd.GeoDataFrame:
    """
    Combining CRIME and SPA processed datasets, and processing it further.
    This function performs a spatial join between the crime dataset and the SPA dataset, and processes this
    combined dataset by handling duplicate rows and unmatched rows. This function then writes this new dataset to a
    GeoJSON file in the data/processed folder.
    This joined dataset is necessary because the CRIME dataset does not contain an SPA column, and I would like to
    analyze crime locations at the SPA level as well.
    :return: gpd.GeoDataFrame
    """
    # Reads the processed crime dataset and puts it into a pandas dataframe
    results_df = pd.read_json("../data/processed/crime_data_processed.json", dtype={"time_occ": str, "date_occ": str})

    # Converting the crime dataframe into a geodataframe based on the latitude and longitude columns.
    gdf_crime = gpd.GeoDataFrame(results_df, geometry=gpd.points_from_xy(results_df.lon, results_df.lat))
    gdf_crime.set_crs("EPSG:4326", inplace=True)
    gdf_crime = gdf_crime.to_crs("EPSG:2229")

    # Reading the processed district dataset and putting it into a GeoData Frame.
    gdf_spa = gpd.read_file("../data/processed/spa_data_processed.geojson")

    # Performs spatial join between the now geospatial crime dataset and the geospatial SPA dataset.
    # The "within" predicate means that if a crime incident location is within an SPA boundary coordinates,
    # then those two rows are joined together.
    gdf_joined_crime_spa = gdf_crime.sjoin(gdf_spa, how="left", predicate="within")

    # Checking for any duplicate rows, and removing them if any.
    duplicates = gdf_joined_crime_spa[gdf_joined_crime_spa.duplicated(keep=False)]
    if len(duplicates) > 0:
        gdf_joined_crime_spa.drop_duplicates(keep="first", inplace=True)

    # Checking for any rows with all null values.
    rows_with_all_na = gdf_joined_crime_spa[gdf_joined_crime_spa.isna().all(axis=1)]
    if len(rows_with_all_na) > 0:
        gdf_joined_crime_spa.drop(rows_with_all_na.index, inplace=True)

    # Checking for unmatched rows which may result when performing joins. Dropping them if any.
    right_columns = ["OBJECTID", "SPA_NAME", "LABEL", "ABBV", "SPA_2012", "Shape_Length", "Shape_Area"]
    unmatched_rows = gdf_joined_crime_spa[gdf_joined_crime_spa[right_columns].isna().all(axis=1)]
    gdf_joined_crime_spa.drop(unmatched_rows.index, inplace=True)

    # Writing processed data to GeoJSON file in the data/prcessed folder.
    processed_combined_crime_districts = os.path.join(
        processed_data_folder, "combined_crime_spa_data_processed.geojson"
    )
    gdf_joined_crime_spa.to_file(processed_combined_crime_districts, driver="GeoJSON")

    return gdf_joined_crime_spa


def csa_data_clean() -> None:
    """
    Data cleaning and processing on COUNTYWIDE STATISTICAL AREAS (CSA) DATA.
    I am considering CSAs because the poverty dataset contains CSA information, and hence I am analyzing crime and
    poverty at the CSA geographical level.
    CSAs in Los Angeles includes both incorporated and unincorporated areas
    Removes the CSAs which are not land, as they are not relevant. This function then creates a GeoJSON file with
    the same data in the data/processed folder.
    The coordinate reference system is 2229, and hence, the Shape.STArea() column is in sqaure feet.
    :return: None
    """
    gdf_csa = gpd.read_file("../data/raw/csa_data.geojson")
    gdf_csa_filtered = gdf_csa[gdf_csa["Feat_Type"] == "Land"].copy()
    processed_csa = os.path.join(processed_data_folder, "csa_data_processed.geojson")
    gdf_csa_filtered.to_file(processed_csa, driver="GeoJSON")


def combining_crime_and_csa_data() -> gpd.GeoDataFrame:
    """
    Combining CRIME and CSA processed datasets, and processing it further.
    This joined dataset is necessary because the CRIME dataset does not contain a CSA column, and I would like to
    analyze crime locations at the CSA level as well.
    This function performs a spatial join between the crime dataset and the CSA dataset, and processes this
    combined dataset by handling duplicate rows and unmatched rows. This function then writes this new dataset to a
    GeoJSON file in the data/processed folder.
    :return: gpd.GeoDataFrame
    """
    # Reads the processed crime dataset and puts it into a pandas dataframe
    results_df = pd.read_json("../data/processed/crime_data_processed.json", dtype={"time_occ": str, "date_occ": str})

    # Converting the crime dataframe into a geodataframe based on the latitude and longitude columns.
    gdf_crime = gpd.GeoDataFrame(results_df, geometry=gpd.points_from_xy(results_df.lon, results_df.lat))
    gdf_crime.set_crs("EPSG:4326", inplace=True)
    gdf_crime = gdf_crime.to_crs("EPSG:2229")

    # Reading the processed csa dataset and putting it into a GeoData Frame.
    gdf_csa_filtered = gpd.read_file("../data/processed/csa_data_processed.geojson")

    # Performs spatial join between the now geospatial crime dataset and the geospatial csa dataset.
    # The "within" predicate means that if a crime incident location is within an SPA boundary coordinates,
    # then those two rows are joined together.
    gdf_joined_crime_csa = gdf_crime.sjoin(gdf_csa_filtered, how="left", predicate="within")

    # Checking for any duplicate rows, and removing them if any.
    duplicates = gdf_joined_crime_csa[gdf_joined_crime_csa.duplicated(keep=False)]
    if len(duplicates) > 0:
        gdf_joined_crime_csa.drop_duplicates(keep="first", inplace=True)

    # Checking for any rows with all null values.
    rows_with_all_na = gdf_joined_crime_csa[gdf_joined_crime_csa.isna().all(axis=1)]
    if len(rows_with_all_na) > 0:
        gdf_joined_crime_csa.drop(rows_with_all_na.index, inplace=True)

    # Checking for unmatched rows which may result when performing joins. Dropping them if any.
    right_columns = [
        "OBJECTID",
        "CITY_TYPE",
        "LCITY",
        "COMMUNITY",
        "LABEL",
        "SOURCE",
        "Shape.STArea()",
        "Shape.STLength()",
        "Feat_Type",
    ]

    unmatched_rows = gdf_joined_crime_csa[gdf_joined_crime_csa[right_columns].isna().all(axis=1)]
    gdf_joined_crime_csa.drop(unmatched_rows.index, inplace=True)

    # Writing processed data to GeoJSON file in the data/prcessed folder.
    processed_combined_crime_csa = os.path.join(processed_data_folder, "combined_crime_csa_data_processed.geojson")
    gdf_joined_crime_csa.to_file(processed_combined_crime_csa, driver="GeoJSON")

    return gdf_joined_crime_csa


def unemployment_data_clean() -> gpd.GeoDataFrame:
    """
    Data cleaning and processing on UNEMPLOYMENT DATA.
    This function processes/cleans the unemployment dataset by removing duplicate rows and rows with all null values.
    The function then writes the processed data to a GeoJSON file in the data/processed folder.
    :return: gpd.GeoDataFrame
    """
    # Reading unemployment raw data and putting it into a geodataframe.
    gdf_unemployment = gpd.read_file("../data/raw/unemployment_data.geojson")

    # Removing duplicate rows in the joined dataset.
    duplicates = gdf_unemployment[gdf_unemployment.duplicated(keep=False)]
    if len(duplicates) > 0:
        gdf_unemployment.drop_duplicates(keep="first", inplace=True)

    # Checking for any rows with all null values.
    rows_with_all_na = gdf_unemployment[gdf_unemployment.isna().all(axis=1)]
    if len(rows_with_all_na) > 0:
        gdf_unemployment.drop(rows_with_all_na.index, inplace=True)

    # Removing rows where unemployment is null.
    rows_with_unemployment_equalto_na = gdf_unemployment[gdf_unemployment["unemployment"].isna()]
    gdf_unemployment.drop(rows_with_unemployment_equalto_na.index, inplace=True)

    # Writing processed data to GeoJSON file in the data/processed folder.
    processed_unemployment = os.path.join(processed_data_folder, "unemployment_data_processed.geojson")
    gdf_unemployment.to_file(processed_unemployment, driver="GeoJSON")

    return gdf_unemployment


results_df_ = crime_data_clean()
gdf_poverty_ = poverty_data_clean()
district_data_clean()
spa_data_clean()
csa_data_clean()
gdf_joined_crime_districts_ = combining_crime_and_district_data()
gdf_joined_crime_spa_ = combining_crime_and_spa_data()
gdf_joined_crime_csa_ = combining_crime_and_csa_data()
gdf_unemployment_ = unemployment_data_clean()

# The below code prints information for each processed dataset.
# This process is helpful to make sure that processing/cleaning performed properly.
print("crime data cleaned")
results_df_.info()
print("-----------------------------------------------------------------")
for item in results_df_.columns:
    print(item)
    print(results_df_[item].unique())
    print("-----------------------------------------------------------------")

print("-----------------------------------------------------------------")
print("poverty data cleaned")
gdf_poverty_.info()
print("-----------------------------------------------------------------")

print("gdf_joined_crime_districts_")
gdf_joined_crime_districts_.info()
print("-----------------------------------------------------------------")


print("gdf_joined_crime_spa_")
gdf_joined_crime_spa_.info()
print("-----------------------------------------------------------------")

print("gdf_joined_crime_csa_")
gdf_joined_crime_csa_.info()
print("-----------------------------------------------------------------")

print("gdf_unemployment")
gdf_unemployment_.info()
print("-----------------------------------------------------------------")
