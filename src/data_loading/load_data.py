from src.data_preprocessing.preprocessing import load_data, get_ISO3, clean_country_names, merge_data, clean_demographics_data, clean_economy_data, clean_geography_data, clean_government_data, clean_transportation_data

data_dict = load_data()

def load_data_into_df():
    data_dict["geography_data"] = clean_geography_data(data_dict["geography_data"])
    data_dict["government_and_civics_data"] = clean_government_data(data_dict["government_and_civics_data"])
    data_dict["transportation_data"] = clean_transportation_data(data_dict["transportation_data"])
    data_dict["demographics_data"] = clean_demographics_data(data_dict["demographics_data"])
    data_dict["economy_data"] = clean_economy_data(data_dict["economy_data"])

    merged_data = merge_data(data_dict)
    merged_data = clean_country_names(merged_data)

    return merged_data

