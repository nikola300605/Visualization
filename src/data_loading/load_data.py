from src.data_preprocessing.preprocessing import load_data, load_external_data, clean_country_names, merge_data, clean_demographics_data, clean_economy_data, clean_geography_data, clean_government_data, clean_transportation_data
import pandas as pd

def load_data_into_df():
    # load fresh copy of raw csvs each time to avoid mutating a shared module-level dict
    data_dict = load_data()

    data_dict["geography_data"] = clean_geography_data(data_dict["geography_data"])
    data_dict["government_and_civics_data"] = clean_government_data(data_dict["government_and_civics_data"])
    data_dict["transportation_data"] = clean_transportation_data(data_dict["transportation_data"])
    data_dict["demographics_data"] = clean_demographics_data(data_dict["demographics_data"])
    data_dict["economy_data"] = clean_economy_data(data_dict["economy_data"])

    external_data = load_external_data()
    merged_external = merge_data(external_data, key="ISO3")

    merged_data = merge_data(data_dict)
    merged_data = clean_country_names(merged_data)

    merged_data = pd.merge(
        merged_data,
        merged_external,
        how="left",
        left_on="ISO3",
        right_on="ISO3"
    )
    for col in merged_data.columns:
        print(col, " - ", merged_data[col].dtype)

    return merged_data

