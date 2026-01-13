from src.data_preprocessing.preprocessing import load_data, load_external_data, clean_country_names, merge_data, clean_demographics_data, clean_economy_data, clean_geography_data, clean_government_data, clean_transportation_data, derive_new_metrics, clean_communications_data
import pandas as pd

def load_data_into_df():
    # load fresh copy of raw csvs each time to avoid mutating a shared module-level dict
    data_dict = load_data()

    data_dict["geography_data"] = clean_geography_data(data_dict["geography_data"])
    data_dict["government_and_civics_data"] = clean_government_data(data_dict["government_and_civics_data"])
    data_dict["transportation_data"] = clean_transportation_data(data_dict["transportation_data"])
    data_dict["demographics_data"] = clean_demographics_data(data_dict["demographics_data"])
    data_dict["economy_data"] = clean_economy_data(data_dict["economy_data"])
    data_dict['communications_data'] = clean_communications_data(data_dict['communications_data'])

    external_data = load_external_data()
    merged_external = merge_data(external_data, key="ISO3")

    merged_data = merge_data(data_dict)

    ### Removing Continents and Oceans and whatnot - shit is fucking up some data
    removed_countries = merged_data['Country'].isin([
        "ANTARCTICA",
        "ARCTIC OCEAN",
        "ATLANTIC OCEAN",
        "PACIFIC OCEAN",
        "UNITED STATES PACIFIC ISLAND WILDLIFE REFUGES",
        "WORLD",
        "EUROPEAN UNION",
        "TOKELAU"
    ])

    merged_data = merged_data[~removed_countries]


    merged_data = clean_country_names(merged_data)
    merged_data = merged_data.drop(columns=["Population_Growth_Rate [%]"])

    merged_data = pd.merge(
        merged_data,
        merged_external,
        how="left",
        left_on="ISO3",
        right_on="ISO3"
    )
    merged_data = derive_new_metrics(merged_data)
    for col in merged_data.columns:
        print(col, " - ", merged_data[col].dtype)

    return merged_data

