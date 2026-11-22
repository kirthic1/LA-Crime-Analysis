import pandas as pd
import geopandas as gpd
from prettytable import PrettyTable
from typing import Tuple

# Reads the processed/cleaned LA crime data and puts it into a pandas dataframe.
results_df = pd.read_json("../data/processed/crime_data_processed.json", dtype={"time_occ": str, "date_occ": str})

# Reads the LA poverty dataset and puts into a geopandas dataframe.
# Adds a column to the poverty geopandas dataframe called "weighted_below_fpl"
# fpl - federal poverty line
# "weighted_below_fpl" = (below_fpl_pct/100) * fpl_universe
# This gives number of people below the fpl.
# This will later be aggregated and used to calculate a weighted poverty level for each district, spa, or csa.
gdf_poverty = gpd.read_file("../data/processed/poverty_data_processed.geojson")
gdf_poverty["weighted_below_fpl"] = (gdf_poverty["below_fpl_pct"] / 100) * gdf_poverty["fpl_universe"]

# Reads processed district, csa, spa, unemployment, and joined datasets and puts each into a geopandas dataframe.
gdf_districts = gpd.read_file("../data/processed/districts_data_processed.geojson")
gdf_csa_filtered = gpd.read_file("../data/processed/csa_data_processed.geojson")
gdf_joined_crime_districts = gpd.read_file("../data/processed/combined_crime_districts_data_processed.geojson")
gdf_joined_crime_spa = gpd.read_file("../data/processed/combined_crime_spa_data_processed.geojson")
gdf_spa = gpd.read_file("../data/processed/spa_data_processed.geojson")
gdf_unemployment = gpd.read_file("../data/processed/unemployment_data_processed.geojson")
gdf_joined_crime_csa = gpd.read_file("../data/processed/combined_crime_csa_data_processed.geojson")


def count_of_incidents_per_year() -> PrettyTable:
    """
    Creates and returns a PrettyTable with the number of crime incidents per year in Los Angeles.
    PrettyTable was used to output a properly formatted table in Pycharm
    :return: PrettyTable
    """
    title1 = "Number of crime incidents per year"
    print(title1)
    count_of_incidents_per_year_data = pd.DataFrame(results_df.groupby(["year"])["dr_no"].count()).reset_index()
    count_of_incidents_per_year_data = count_of_incidents_per_year_data.rename(
        columns={"dr_no": "Number of crime " "incidents"}
    )
    table = PrettyTable()
    table.field_names = count_of_incidents_per_year_data.columns
    for row in count_of_incidents_per_year_data.itertuples(index=False, name=None):
        table.add_row(list(row))
    return table


def count_of_incidents_per_month() -> PrettyTable:
    """
    Creates and returns a PrettyTable with the number of crime incidents per month in Los Angeles.
    :return: PrettyTable
    """
    title2 = "Number of incidents per month"
    print(title2)
    count_of_incidents_per_month_data = pd.DataFrame(results_df.groupby(["month"])["dr_no"].count()).reset_index()
    count_of_incidents_per_month_data = count_of_incidents_per_month_data.rename(
        columns={"dr_no": "Number of crime " "incidents"}
    )
    table = PrettyTable()
    table.field_names = count_of_incidents_per_month_data.columns
    for row in count_of_incidents_per_month_data.itertuples(index=False, name=None):
        table.add_row(list(row))
    return table


def victim_age_demographics() -> PrettyTable:
    """
    Creates and returns a PrettyTable with the top 5 age groups that have most frequently been the victims of crime
    incidents in Los Angeles.
    :return: PrettyTable
    """
    title3 = "Most targeted victim age groups. O is Unknown Age"
    print(title3)
    top_5_ages = results_df.groupby("vict_age")["dr_no"].count().nlargest(5)
    top_5_ages_df = pd.DataFrame(top_5_ages).reset_index()
    top_5_ages_df = top_5_ages_df.rename(columns={"dr_no": "Number of crime incidents", "vict_age": "Victim Age"})
    table = PrettyTable()
    table.field_names = top_5_ages_df.columns
    for row in top_5_ages_df.itertuples(index=False, name=None):
        table.add_row(list(row))
    return table


def victim_descent_demographics() -> PrettyTable:
    """
    Creates and returns a PrettyTable with the top 5 victim descent groups that have been targeted most by crime in
    Los Angeles.
    :return: PrettyTable
    """
    title4 = "Most targeted victim descent groups"
    print(title4)
    top_5_descent = results_df.groupby("vict_descent")["dr_no"].count().nlargest(5)
    top_5_descent_df = pd.DataFrame(top_5_descent).reset_index()
    top_5_descent_df = top_5_descent_df.rename(
        columns={"dr_no": "Number of crime incidents", "vict_descent": "Victim Descent"}
    )
    victim_descent = {
        "A": "Other Asian",
        "B": "Black",
        "C": "Chinese",
        "D": "Cambodian",
        "F": "Filipino",
        "G": "Guamanian",
        "H": "Hispanic/Latin/Mexican",
        "I": "American Indian/Alaskan Native",
        "J": "Japanese",
        "K": "Korean",
        "L": "Laotian",
        "O": "Other",
        "P": "Pacific Islander",
        "S": "Samoan",
        "U": "Hawaiian",
        "V": "Vietnamese",
        "W": "White",
        "X": "Unknown",
        "Z": "Asian Indian",
    }
    victim_descent_code = pd.DataFrame.from_dict(
        victim_descent, orient="index", columns=["Victim Descent description"]
    ).reset_index()
    victim_descent_code = victim_descent_code.rename(columns={"index": "Victim Descent"})
    top_5_descent_df_with_description = pd.merge(top_5_descent_df, victim_descent_code, how="left", on="Victim Descent")
    table = PrettyTable()
    table.field_names = top_5_descent_df_with_description.columns
    for row in top_5_descent_df_with_description.itertuples(index=False, name=None):
        table.add_row(list(row))
    return table


def crime_incident_status_statistics() -> PrettyTable:
    """
    Creates and returns a PrettyTable with the top 5 crime incident statuses to understand how the crimes are being
    handled/taken care of.
    :return: PrettyTable
    """
    title5 = "Count of crime incident statuses"
    print(title5)
    count_of_crime_incident_statuses = results_df.groupby("status_desc")["dr_no"].count()
    count_of_crime_incident_statuses_df = pd.DataFrame(count_of_crime_incident_statuses).reset_index()
    count_of_crime_incident_statuses_df = count_of_crime_incident_statuses_df.rename(
        columns={"status_desc": "Crime Incident Status Description", "dr_no": "Number of crime incidents"}
    )
    count_of_crime_incident_statuses_df = count_of_crime_incident_statuses_df.sort_values(
        by="Number of crime incidents", ascending=False
    )
    table = PrettyTable()
    table.field_names = count_of_crime_incident_statuses_df.columns
    for row in count_of_crime_incident_statuses_df.itertuples(index=False, name=None):
        table.add_row(list(row))
    return table


def weapon_statistics() -> Tuple[pd.DataFrame, PrettyTable]:
    """
    Creates and returns a dataframe and PrettyTable with the top 10 most frequently used weapons in crime incidents
    in Los Angeles. Returning a dataframe as well as it will be used in following analyses. This is helpful for
    police to be prepared with defense mechanisms for these weapons.
    :return: Tuple[pd.DataFrame, PrettyTable]
    """
    weapon_counts = results_df.groupby("weapon_desc")["dr_no"].count().nlargest(10)
    top_10_weapon_counts = pd.DataFrame(weapon_counts).reset_index()
    top_10_weapon_counts = top_10_weapon_counts.rename(
        columns={"weapon_desc": "Weapon Description", "dr_no": "Number of crime incidents"}
    )
    table = PrettyTable()
    table.field_names = top_10_weapon_counts.columns
    for row in top_10_weapon_counts.itertuples(index=False, name=None):
        table.add_row(list(row))
    return top_10_weapon_counts, table


def type_of_crime_statistics() -> Tuple[pd.DataFrame, PrettyTable]:
    """
    Creates and returns a dataframe and PrettyTable with the top 10 most frequent types of crime in Los Angeles.
    :return: Tuple[pd.DataFrame, PrettyTable]
    """
    type_of_crime_counts = results_df.groupby("crm_cd_desc")["dr_no"].count()
    top_10_crime_counts = type_of_crime_counts.nlargest(10)
    top_10_crime_counts_df = pd.DataFrame(top_10_crime_counts).reset_index()
    top_10_crime_counts_df = top_10_crime_counts_df.rename(
        columns={"crm_cd_desc": "Type of Crime", "dr_no": "Number of crime incidents"}
    )
    table = PrettyTable()
    table.field_names = top_10_crime_counts_df.columns
    for row in top_10_crime_counts_df.itertuples(index=False, name=None):
        table.add_row(list(row))
    return top_10_crime_counts_df, table


def mocodes_statistics() -> Tuple[pd.DataFrame, PrettyTable]:
    """
    Creates and returns a dataframe and PrettyTable with the top 10 most frequent mocodes.
    Mocodes are codes that describe how the suspect behaves.
    :return: Tuple[pd.DataFrame, PrettyTable]
    """
    list_of_mocodes = []
    results_df["mocodes"].apply(lambda x: list_of_mocodes.extend(x.split()))
    mocodes_series = pd.Series(list_of_mocodes)
    mocodes_count = mocodes_series.value_counts()
    top_10_mocodes = mocodes_count.nlargest(10)
    top_10_mocodes_df = pd.DataFrame(top_10_mocodes).reset_index()
    top_10_mocodes_df = top_10_mocodes_df.rename(columns={"index": "Mocode", "count": "Number of crime incidents"})
    table = PrettyTable()
    table.field_names = top_10_mocodes_df.columns
    for row in top_10_mocodes_df.itertuples(index=False, name=None):
        table.add_row(list(row))
    return top_10_mocodes_df, table


def premise_statistics() -> Tuple[pd.DataFrame, PrettyTable]:
    """
    Creates and returns a dataframe and PrettyTable with the top 10 most common premise areas where crimes in Los
    Angeles have occurred.
    The metadata describes premise as "the type of structure, vehicle, or location where the crime took place."
    :return: Tuple[pd.DataFrame, PrettyTable]
    """
    count_of_incidents_per_premise_top_10 = results_df.groupby(["premis_desc"])["dr_no"].count().nlargest(10)
    count_of_incidents_per_premise_df_top10 = pd.DataFrame(count_of_incidents_per_premise_top_10).reset_index()
    count_of_incidents_per_premise_df_top10 = count_of_incidents_per_premise_df_top10.rename(
        columns={"dr_no": "Number of crime " "incidents"}
    )
    table = PrettyTable()
    table.field_names = count_of_incidents_per_premise_df_top10.columns
    for row in count_of_incidents_per_premise_df_top10.itertuples(index=False, name=None):
        table.add_row(list(row))
    return count_of_incidents_per_premise_df_top10, table


def victim_gender_analysis() -> Tuple[pd.DataFrame, PrettyTable]:
    """
    Creates and returns a dataframe and PrettyTable with the number of crime incidents in Los Angeles that targeted
    each gender.
    :return: Tuple[pd.DataFrame, PrettyTable]
    """
    title6 = "Number of crime incidents per gender"
    print(title6)
    victim_gender_count = results_df.groupby(["vict_sex"])["dr_no"].count()
    victim_gender_count_df = pd.DataFrame(victim_gender_count).reset_index()
    table = PrettyTable()
    table.field_names = victim_gender_count_df.columns
    for row in victim_gender_count_df.itertuples(index=False, name=None):
        table.add_row(list(row))
    return victim_gender_count_df, table


def district_analysis() -> Tuple[pd.DataFrame, PrettyTable]:
    """
    Creates and returns a dataframe and PrettyTable with the crime density in each district in Los Angeles.
    To calculate crime density for each district, this function obtains the total number of crimes per district using
    the joined crime_district table, and divides that value by the Shape Area from the districts table.
    This calculation is performed for each district.
    The coordinate reference system for gdf_districts is 2229, and hence, the Shape.STArea() column is in sqaure feet.
    :return: Tuple[pd.DataFrame, PrettyTable]
    """
    district_shape_area = gdf_districts[["Shape.STArea()", "DISTRICT"]].copy()
    crime_density_df = pd.DataFrame(gdf_joined_crime_districts.groupby("DISTRICT")["dr_no"].count()).reset_index()
    crime_density_df_final = pd.merge(crime_density_df, district_shape_area, how="left", on="DISTRICT")
    crime_density_df_final["crime density (crimes per square foot)"] = (
        crime_density_df_final["dr_no"] / crime_density_df_final["Shape.STArea()"]
    )
    table = PrettyTable()
    table.field_names = crime_density_df_final.columns
    for row in crime_density_df_final.itertuples(index=False, name=None):
        table.add_row(list(row))
    return crime_density_df_final, table


def part1_part2_crimes_analysis() -> Tuple[pd.DataFrame, PrettyTable]:
    """
    Creates and returns a dataframe and PrettyTable that lists the percentage of part 1 and part 2 crimes in each
    district in Los Angeles.
    The metadata describes Part 1 crimes as more violent/serious than part 2 crimes.
    :return: Tuple[pd.DataFrame, PrettyTable]
    """
    part1_part2_crimes_per_district = pd.DataFrame(
        gdf_joined_crime_districts.groupby(["DISTRICT", "part_1_2"])["dr_no"].count()
    )
    part1_part2_crimes_per_district = part1_part2_crimes_per_district.reset_index()

    crime_density_df_final, table = district_analysis()

    part1_part2_crimes_per_district_percentage_analysis = pd.merge(
        part1_part2_crimes_per_district, crime_density_df_final, how="left", on="DISTRICT"
    )

    part1_part2_crimes_per_district_percentage_analysis["Percentage of part 1 and part 2 crimes in this district"] = (
        part1_part2_crimes_per_district_percentage_analysis["dr_no_x"]
        / part1_part2_crimes_per_district_percentage_analysis["dr_no_y"]
    ) * 100

    part1_part2_crimes_per_district_percentage_analysis = part1_part2_crimes_per_district_percentage_analysis.rename(
        columns={
            "dr_no_x": "Total number of part 1 and part 2 crimes per district",
            "dr_no_y": "Total number of crimes per district",
        }
    )
    table = PrettyTable()
    table.field_names = part1_part2_crimes_per_district_percentage_analysis.columns
    for row in part1_part2_crimes_per_district_percentage_analysis.itertuples(index=False, name=None):
        table.add_row(list(row))
    return part1_part2_crimes_per_district_percentage_analysis, table


def poverty_and_district_crime() -> Tuple[pd.DataFrame, PrettyTable]:
    """
    Creates and returns a dataframe and PrettyTable where crime density and weighted poverty level is calculated for
    each  district in Los Angeles.
    :return: Tuple[pd.DataFrame, PrettyTable]
    """
    # Calculating the total fpl universe for each district using the poverty dataset.
    total_fpl_universe = pd.DataFrame(gdf_poverty.groupby("sup_dist")["fpl_universe"].sum()).reset_index()

    # Calculating total number of people below the fpl for each district using the poverty dataset.
    weighted_below_fpl_sum = pd.DataFrame(gdf_poverty.groupby("sup_dist")["weighted_below_fpl"].sum()).reset_index()

    # Merging the total_fpl_universe and weighted_below_fpl_sum dataframes together
    weighted_poverty_per_district = pd.merge(total_fpl_universe, weighted_below_fpl_sum, how="left", on="sup_dist")

    # Calculating the weighted poverty level for each district.
    weighted_poverty_per_district["weighted poverty"] = (
        weighted_poverty_per_district["weighted_below_fpl"] / weighted_poverty_per_district["fpl_universe"]
    ) * 100

    weighted_poverty_per_district = weighted_poverty_per_district.rename(columns={"sup_dist": "DISTRICT"})
    weighted_poverty_per_district["DISTRICT"] = pd.Series(["1", "2", "3", "4", "5"])

    crime_density_df_final, table = district_analysis()

    # Merges the crime_density_df_final table from the district_analysis() with weighted_poverty_per_district table.
    poverty_and_crime_district_analysis = pd.merge(
        weighted_poverty_per_district, crime_density_df_final, how="left", on="DISTRICT"
    )

    table = PrettyTable()
    table.field_names = poverty_and_crime_district_analysis.columns
    for row in poverty_and_crime_district_analysis.itertuples(index=False, name=None):
        table.add_row(list(row))
    return poverty_and_crime_district_analysis, table


def spa_analysis() -> Tuple[pd.DataFrame, PrettyTable]:
    """
    Creates and returns a dataframe and PrettyTable where crime density is calculated for each SPA in Los Angeles.
    This is another geographical scale that will give insights into level of crime in each SPA.
    :return: Tuple[pd.DataFrame, PrettyTable]
    """
    spa_crime_density = pd.DataFrame(gdf_joined_crime_spa.groupby("ABBV")["dr_no"].count()).reset_index()
    spa_shape_area = gdf_spa[["Shape_Area", "ABBV"]].copy()
    spa_crime_density_final = pd.merge(spa_crime_density, spa_shape_area, how="outer", on="ABBV")
    spa_crime_density_final["crime density (crimes per square foot)"] = (
        spa_crime_density_final["dr_no"] / spa_crime_density_final["Shape_Area"]
    )
    spa_crime_density_final = spa_crime_density_final.fillna(0)

    table = PrettyTable()
    table.field_names = spa_crime_density_final.columns
    for row in spa_crime_density_final.itertuples(index=False, name=None):
        table.add_row(list(row))
    return spa_crime_density_final, table


def poverty_and_spa_crime() -> Tuple[pd.DataFrame, PrettyTable]:
    """
    Creates and returns a dataframe and PrettyTable where crime density and weighted poverty level is calculated for
    each SPA in Los Angeles.
    :return: Tuple[pd.DataFrame, PrettyTable]
    """
    # Calculating the total fpl universe for each SPA using the poverty dataset.
    total_fpl_universe = pd.DataFrame(gdf_poverty.groupby("spa")["fpl_universe"].sum()).reset_index()

    # Calculating total number of people below the fpl for each SPA using the poverty dataset.
    weighted_below_fpl_sum = pd.DataFrame(gdf_poverty.groupby("spa")["weighted_below_fpl"].sum()).reset_index()

    # Merging the total_fpl_universe and weighted_below_fpl_sum dataframes together
    weighted_poverty_per_spa = pd.merge(total_fpl_universe, weighted_below_fpl_sum, how="left", on="spa")

    # Calculating the weighted poverty level for each SPA.
    weighted_poverty_per_spa["weighted poverty"] = (
        weighted_poverty_per_spa["weighted_below_fpl"] / weighted_poverty_per_spa["fpl_universe"]
    ) * 100

    weighted_poverty_per_spa = weighted_poverty_per_spa.rename(columns={"spa": "ABBV"})
    weighted_poverty_per_spa["ABBV"] = pd.Series(
        ["SPA 1", "SPA 2", "SPA 3", "SPA 4", "SPA 5", "SPA 6", "SPA 7", "SPA 8"]
    )

    spa_crime_density_final, table = spa_analysis()

    # Merges the spa_crime_density_final table from the spa_analysis() with weighted_poverty_per_spa table.
    poverty_and_crime_spa_analysis = pd.merge(weighted_poverty_per_spa, spa_crime_density_final, how="left", on="ABBV")

    table = PrettyTable()
    table.field_names = poverty_and_crime_spa_analysis.columns
    for row in poverty_and_crime_spa_analysis.itertuples(index=False, name=None):
        table.add_row(list(row))
    return poverty_and_crime_spa_analysis, table


def unemployment_analysis() -> Tuple[pd.DataFrame, PrettyTable]:
    """
    Creates and returns a dataframe and PrettyTable where crime density and average unemployment level is calculated
    for each district in Los Angeles.
    :return: Tuple[pd.DataFrame, PrettyTable]
    """
    average_unemployment = pd.DataFrame(gdf_unemployment.groupby("sup_dist")["unemployment"].mean())
    average_unemployment = average_unemployment.reset_index()
    average_unemployment = average_unemployment.rename(columns={"sup_dist": "DISTRICT"})
    average_unemployment["DISTRICT"] = pd.Series(["1", "2", "3", "4", "5"])
    crime_density_df_final, crime_density_table = district_analysis()
    unemployment_and_crime_graph = pd.merge(crime_density_df_final, average_unemployment, how="left", on="DISTRICT")
    table = PrettyTable()
    table.field_names = unemployment_and_crime_graph.columns
    for row in unemployment_and_crime_graph.itertuples(index=False, name=None):
        table.add_row(list(row))
    return unemployment_and_crime_graph, table


def csa_analysis() -> Tuple[pd.DataFrame, PrettyTable]:
    """
    Creates and returns a dataframe and PrettyTable where crime density is calculated for each csa in Los Angeles.
    :return: Tuple[pd.DataFrame, PrettyTable]
    """
    csa_crime_density = pd.DataFrame(gdf_joined_crime_csa.groupby("LABEL")["dr_no"].count()).reset_index()
    csa_shape_area = gdf_csa_filtered[["Shape.STArea()", "LABEL"]].copy()
    csa_crime_density_final = pd.merge(csa_crime_density, csa_shape_area, how="left", on="LABEL")
    csa_crime_density_final["crime density (crimes per square foot)"] = (
        csa_crime_density_final["dr_no"] / csa_crime_density_final["Shape.STArea()"]
    )
    table = PrettyTable()
    table.field_names = csa_crime_density_final.columns
    for row in csa_crime_density_final.itertuples(index=False, name=None):
        table.add_row(list(row))
    return csa_crime_density_final, table


def csa_crime_poverty_data() -> Tuple[pd.DataFrame, PrettyTable]:
    """
    Creates and returns a dataframe and PrettyTable where crime density and weighted poverty level is calculated for
    each csa in Los Angeles.
    :return: Tuple[pd.DataFrame, PrettyTable]
    """
    # Total fpl_universe is calculated for each csa using the poverty dataset.
    total_fpl_universe_csa = pd.DataFrame(gdf_poverty.groupby("csa")["fpl_universe"].sum())
    total_fpl_universe_csa = total_fpl_universe_csa.reset_index()

    # Total number of people below the fpl is calculated for each csa using the poverty dataset.
    weighted_below_fpl_sum_csa = pd.DataFrame(gdf_poverty.groupby("csa")["weighted_below_fpl"].sum())
    weighted_below_fpl_sum_csa = weighted_below_fpl_sum_csa.reset_index()

    # The total_fpl_universe_csa and the weighted_below_fpl_sum_csa are merged together.
    csa_poverty_data = pd.merge(weighted_below_fpl_sum_csa, total_fpl_universe_csa, how="left", on="csa")

    # Calculates the weighted povertly level for each csa.
    csa_poverty_data["Weighted Poverty Level"] = (
        csa_poverty_data["weighted_below_fpl"] / csa_poverty_data["fpl_universe"]
    ) * 100
    csa_poverty_data = csa_poverty_data.rename(columns={"csa": "LABEL"})

    csa_crime_density_final, table = csa_analysis()

    # Merging the csa_crime_density_final which has the crime densities of the csa's with the csa_poverty_data which
    # has the weighted poverty levels of the csa's.
    csa_poverty_and_crime_density_data = pd.merge(csa_crime_density_final, csa_poverty_data, how="left", on="LABEL")

    # Checking and handling any unmatched rows in the merged datasets of csa_crime_density_final and
    # csa_poverty_and_crime_density_data
    right_columns = ["weighted_below_fpl", "fpl_universe", "Weighted Poverty Level"]
    unmatched_rows = csa_poverty_and_crime_density_data[
        csa_poverty_and_crime_density_data[right_columns].isna().all(axis=1)
    ]
    csa_poverty_and_crime_density_data.drop(unmatched_rows.index, inplace=True)

    # Choosing only the csa's which have enough number (atleast 10) of census tracts in the poverty dataset to obtain
    # an accurate estimate of the weighted poverty level of the csa. This is basically to ensure there is a good
    # sample size.
    csa_to_consider = []
    for element in gdf_joined_crime_csa["LABEL"].unique():
        if len(gdf_poverty[gdf_poverty["csa"] == element]) >= 10:
            csa_to_consider.append(element)
    csa_poverty_and_crime_density_data_filtered = csa_poverty_and_crime_density_data[
        csa_poverty_and_crime_density_data["LABEL"].isin(csa_to_consider)
    ].copy()

    table = PrettyTable()
    table.field_names = csa_poverty_and_crime_density_data_filtered
    for row in csa_poverty_and_crime_density_data_filtered.itertuples(index=False, name=None):
        table.add_row(list(row))
    return csa_poverty_and_crime_density_data_filtered, table


def csa_crime_unemployment_data() -> Tuple[pd.DataFrame, PrettyTable]:
    """
    Creates and returns a dataframe and PrettyTable where crime density and average unemployment level is calculated
    for each csa in Los Angeles.
    :return: Tuple[pd.DataFrame, PrettyTable]
    """
    # Calculating average unemployment for each csa using the unemployment dataset
    average_unemployment = pd.DataFrame(gdf_unemployment.groupby("csa")["unemployment"].mean()).reset_index()
    average_unemployment = average_unemployment.rename(columns={"csa": "LABEL"})

    csa_crime_density_final, table = csa_analysis()

    # Merges the average_unemployment data table with the csa crime density data table.
    csa_unemployment_and_crime_density_data = pd.merge(
        csa_crime_density_final, average_unemployment, how="left", on="LABEL"
    )
    # Checking and handling for unmatched rows
    right_columns = ["unemployment"]
    unmatched_rows = csa_unemployment_and_crime_density_data[
        csa_unemployment_and_crime_density_data[right_columns].isna().all(axis=1)
    ]
    csa_unemployment_and_crime_density_data.drop(unmatched_rows.index, inplace=True)

    # Choosing only the csa's which have enough number (atleast 10) of census tracts in the unemployment dataset to
    # obtain an accurate estimate of the average unemployment level of the csa
    csa_to_consider = []
    for element in gdf_joined_crime_csa["LABEL"].unique():
        if len(gdf_unemployment[gdf_unemployment["csa"] == element]) >= 10:
            csa_to_consider.append(element)
    csa_unemployment_and_crime_density_data_filtered = csa_unemployment_and_crime_density_data[
        csa_unemployment_and_crime_density_data["LABEL"].isin(csa_to_consider)
    ].copy()
    table = PrettyTable()
    table.field_names = csa_unemployment_and_crime_density_data_filtered
    for row in csa_unemployment_and_crime_density_data_filtered.itertuples(index=False, name=None):
        table.add_row(list(row))
    return csa_unemployment_and_crime_density_data_filtered, table


# The below code calls all functions, and prints all dataframes.
df = count_of_incidents_per_year()
print(df)
print("___________________________________")

df1 = count_of_incidents_per_month()
print(df1)
print("___________________________________")

df2 = victim_age_demographics()
print(df2)
print("___________________________________")

df3 = victim_descent_demographics()
print(df3)
print("___________________________________")

df4 = crime_incident_status_statistics()
print(df4)
print("___________________________________")

df5, df5b = weapon_statistics()
title = "Most used types of weapons"
print(title)
print(df5b)
print("___________________________________")

df6, df6b = type_of_crime_statistics()
title = "Top 10 types of crime"
print(title)
print(df6b)
print("___________________________________")

df7, df7b = mocodes_statistics()
title = "Top 10 mocodes"
print(title)
print(df7b)
print("___________________________________")

title = "Top 10 premises where most crimes occur"
print(title)
df8, df8b = premise_statistics()
print(df8b)
print("___________________________________")

df9, df9b = victim_gender_analysis()
print(df9b)
print("___________________________________")

df10, df10b = district_analysis()
title = "Crime Density per district"
print(title)
print(df10b)
print("___________________________________")

df11, df11b = part1_part2_crimes_analysis()
title = "Percentage of part 1 and part 2 crimes out of total crimes in each district"
print(title)
print(df11b)
print("___________________________________")

df12, df12b = poverty_and_district_crime()
title = "Poverty Levels and Crime Density in each district"
print(title)
print(df12b)
print("___________________________________")

df13, df13b = spa_analysis()
title = "Crime density per SPA (Service Planning Area)"
print(title)
print(df13b)
print("___________________________________")

df14, df14b = poverty_and_spa_crime()
title = "Poverty level and crime density in each SPA"
print(title)
print(df14b)
print("___________________________________")

df15, df15b = unemployment_analysis()
title = "Unemployment level and crime density in each district"
print(title)
print(df15b)
print("___________________________________")

df16, df16b = csa_crime_poverty_data()
title = "Weighted Poverty Levels and crime density in multiple CSA's in Los Angeles"
print(title)
print(df16b)

df17, df17b = csa_crime_unemployment_data()
title = "Unemployment Levels and crime density in multiple CSA's in Los Angeles"
print(title)
print(df17b)
