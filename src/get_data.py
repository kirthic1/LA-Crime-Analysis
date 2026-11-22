import requests
from requests.exceptions import RequestException
import os
import geopandas as gpd
import pandas as pd
from typing import Union
from dotenv import load_dotenv

load_dotenv()


# This python script is collecting data by sending requests to 6 APIs in total.
def load_crime_data() -> pd.DataFrame:
    """
    Retrieves Los Angeles CRIME data through API request and writes the data to a JSON file in the data/raw folder.
    This code retrieves the data in sets of 10,000 rows till it reaches end of dataset since the API has querying
    limits.
    :return: pd.DataFrame
    """
    app_token = os.getenv("LA_CRIME_APP_TOKEN")
    headers = {"X-App-Token": app_token} if app_token else {}
    params = {"$limit": 10000}
    url = "https://data.lacity.org/resource/2nrs-mtv8.json"
    data = []
    offset = 0
    raw_data_folder = "../data/raw"
    while True:
        try:
            params["$offset"] = offset
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            print(f"Retrieved 10000 rows. Offset = {offset}")
            results = response.json()
            data.extend(results)
            if len(results) < 10000 or len(results) == 0:
                print("Retrieved all data")
                break
            offset = offset + 10000
        except RequestException:
            raise Exception("Error occurred while fetching data")
        except Exception:
            raise Exception("Error occurred while fetching data")
    results_df = pd.DataFrame(data)
    raw_crime_data = os.path.join(raw_data_folder, "crime_data.json")
    results_df.to_json(raw_crime_data, orient="records", lines=False)
    return results_df


def load_poverty_data() -> gpd.GeoDataFrame:
    """
    Retrieves Los Angeles POVERTY geospatial data through API request and writes the data to a GeoJSON file in the
    data/raw folder.
    This code retrieves the data in sets of 2000 till it reaches end of dataset to avoid overload issues.
    The output spatial reference system is 2229, as this is the most appropriate spatial reference system for local
    Los Angeles data.
    :return: gpd.GeoDataFrame
    """
    url = "https://services.arcgis.com/RmCCgQtiZLDCtblq/arcgis/rest/services/Below_Poverty_tract/FeatureServer/0/query"
    params = {"where": "1=1", "outFields": "*", "f": "geojson", "resultRecordCount": 2000, "outSR": 2229}
    features = []
    offset = 0
    raw_data_folder = "../data/raw"
    while True:
        try:
            params["resultOffset"] = offset
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            features.extend(data["features"])
            if len(data["features"]) < 2000 or len(data["features"]) == 0:
                break
            offset = offset + 2000
        except RequestException:
            raise Exception("Error occurred while fetching data")
        except Exception:
            raise Exception("Error occurred while fetching data")
    gdf_poverty = gpd.GeoDataFrame.from_features(features)
    gdf_poverty.set_crs("EPSG:2229", allow_override=True, inplace=True)
    gdf_poverty["calculated_area"] = gdf_poverty.geometry.area
    raw_poverty_data = os.path.join(raw_data_folder, "poverty_data.geojson")
    gdf_poverty.to_file(raw_poverty_data, driver="GeoJSON")
    return gdf_poverty


def load_district_data() -> gpd.GeoDataFrame:
    """
    Retrieves Los Angeles DISTRICTS geospatial data through API request and writes the data to a GeoJSON file in the
    data/raw folder.
    The output spatial reference system is 2229, as this is the most appropriate spatial reference system for local
    Los Angeles data.
    :return: gpd.GeoDataFrame
    """
    url = (
        "https://arcgis.gis.lacounty.gov/arcgis/rest/services/LACounty_Dynamic/Political_Boundaries/MapServer/27"
        "/query"
    )
    features = []
    params = {"where": "1=1", "outFields": "*", "f": "geojson", "outSR": 2229}
    raw_data_folder = "../data/raw"
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        features.extend(data["features"])
        gdf_district = gpd.GeoDataFrame.from_features(features)
        gdf_district.set_crs("EPSG:2229", allow_override=True, inplace=True)
        gdf_district["calculated_area"] = gdf_district.geometry.area
        raw_district_data = os.path.join(raw_data_folder, "district_data.geojson")
        gdf_district.to_file(raw_district_data, driver="GeoJSON")
    except RequestException:
        raise Exception("Error occurred while fetching data")
    except Exception:
        raise Exception("Error occurred while fetching data")
    return gdf_district


def load_spa_data() -> gpd.GeoDataFrame:
    """
    Retrieves Los Angeles SERVICE PLANNING AREAS (SPA) geospatial data through API request and writes the data to a
    GeoJSON file in the data/raw folder.
    The output spatial reference system is 2229, as this is the most appropriate spatial reference system for local
    Los Angeles data.
    :return: gpd.GeoDataFrame
    """
    url = (
        "https://public.gis.lacounty.gov/public/rest/services/LACounty_Dynamic/Administrative_Boundaries/MapServer"
        "/4/query"
    )
    features = []
    params = {"where": "1=1", "outFields": "*", "f": "geojson", "outSR": 2229}
    raw_data_folder = "../data/raw"
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        features.extend(data["features"])
        gdf_spa = gpd.GeoDataFrame.from_features(features)
        gdf_spa.set_crs("EPSG:2229", allow_override=True, inplace=True)
        gdf_spa["calculated_area"] = gdf_spa.geometry.area
        raw_spa_data = os.path.join(raw_data_folder, "spa_data.geojson")
        gdf_spa.to_file(raw_spa_data, driver="GeoJSON")
    except RequestException:
        raise Exception("Error occurred while fetching data")
    except Exception:
        raise Exception("Error occurred while fetching data")
    return gdf_spa


def load_csa_data() -> gpd.GeoDataFrame:
    """
    Retrieves Los Angeles COUNTYWIDE STATISTICAL AREAS (CSA) geospatial data through API request and writes the data
    to a
    GeoJSON file in the data/raw folder.
    The output spatial reference system is 2229, as this is the most appropriate spatial reference system for local
    Los Angeles data.
    :return: gpd.GeoDataFrame
    """
    url = (
        "https://public.gis.lacounty.gov/public/rest/services/LACounty_Dynamic/Political_Boundaries/MapServer/23"
        "/query"
    )
    features = []
    raw_data_folder = "../data/raw"
    params = {"where": "1=1", "outFields": "*", "f": "geojson", "outSR": 2229}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        features.extend(data["features"])
        gdf_csa = gpd.GeoDataFrame.from_features(features)
        gdf_csa.set_crs("EPSG:2229", allow_override=True, inplace=True)
        gdf_csa["calculated_area"] = gdf_csa.geometry.area
        raw_csa_data = os.path.join(raw_data_folder, "csa_data.geojson")
        gdf_csa.to_file(raw_csa_data, driver="GeoJSON")
    except requests.exceptions.RequestException:
        raise Exception("Error occured while fetching data")
    except Exception:
        raise Exception("Error occured while fetching data")
    return gdf_csa


def load_unemployment_data() -> gpd.GeoDataFrame:
    """
    Retrieves Los Angeles UNEMPLOYMENT geospatial data through API request and writes the data to a GeoJSON file in
    the data/raw folder.
    This code retrieves the data in sets of 2000 till it reaches end of dataset to avoid overload issues.
    The output spatial reference system is 2229, as this is the most appropriate spatial reference system for local
    Los Angeles data.
    :return: gpd.GeoDataFrame
    """
    url = "https://services.arcgis.com/RmCCgQtiZLDCtblq/arcgis/rest/services/Unemployment/FeatureServer/8/query"
    params = {"where": "1=1", "outFields": "*", "f": "geojson", "resultRecordCount": 2000, "outSR": 2229}
    features = []
    offset = 0
    raw_data_folder = "../data/raw"
    while True:
        try:
            params["resultOffset"] = offset
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            features.extend(data["features"])
            if len(data["features"]) < 2000 or len(data["features"]) == 0:
                break
            offset = offset + 2000
        except RequestException:
            raise Exception("Error occurred while fetching data")
        except Exception:
            raise Exception("Error occurred while fetching data")
    gdf_unemployment = gpd.GeoDataFrame.from_features(features)
    gdf_unemployment.set_crs("EPSG:2229", allow_override=True, inplace=True)
    gdf_unemployment["calculated_area"] = gdf_unemployment.geometry.area
    raw_unemployment_data = os.path.join(raw_data_folder, "unemployment_data.geojson")
    gdf_unemployment.to_file(raw_unemployment_data, driver="GeoJSON")
    return gdf_unemployment


results_df_ = load_crime_data()
gdf_poverty_ = load_poverty_data()
gdf_district_ = load_district_data()
gdf_spa_ = load_spa_data()
gdf_csa_ = load_csa_data()
gdf_unemployment_ = load_unemployment_data()


def df_info(df: Union[pd.DataFrame, gpd.GeoDataFrame]) -> None:
    """
    This function provides information using the .info() method about each dataframe that was created for each API data
    source. This is so that the user can see information about each raw dataset
    :param df: The dataframe the user would like information about
    :return: None
    """
    print(df.info())


# The below code calls the df_info function for each raw dataset.
# This process is helpful to see what processing and cleaning is required for each raw dataset.
print("Raw Crime Data Info")
df_info(results_df_)
print("----------------------------------------------")
for item in results_df_.columns:
    print(item)
    print(results_df_[item].unique())
    print("----------------------------------------------")

print("Raw Poverty Data Info")
df_info(gdf_poverty_)
print("-----------------------")

print("Raw District Data Info")
df_info(gdf_district_)
print("-----------------------")


print("Raw Service Planning Areas (SPA) Data Info")
df_info(gdf_spa_)
print("-----------------------")


print("Combined Statistical Area (CSA) Data Info")
df_info(gdf_csa_)
print("-----------------------")


print("Raw Unemployment Data Info")
df_info(gdf_unemployment_)
