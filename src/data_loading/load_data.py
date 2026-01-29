from src.data_preprocessing.preprocessing import load_data, load_external_data, clean_country_names, merge_data, clean_demographics_data, clean_economy_data, clean_geography_data, clean_government_data, clean_transportation_data, derive_new_metrics, clean_communications_data
from src.components.clustering import create_development_clusters_without_analysis
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
    merged_data = create_development_clusters_without_analysis(merged_data, n_clusters=4)

    for col in merged_data.columns:
        print(col, " - ", merged_data[col].dtype)

    return merged_data

df = load_data_into_df()
print(df['Unemployment_Rate_percent'].isna().sum())
features = [
        'Population_Growth_Rate_(percentage)',
        'Real_GDP_per_Capita_USD',
        'Median_Age',
        'Total_Fertility_Rate',
        'Expected_Years_of_Schooling_(years)',
        'Youth_Unemployment_Rate_percent'
    ]

df_clusters = df[features]
missing_pct = df_clusters.isna().sum() / len(df) * 100
print(missing_pct)

df_edited = df.copy()
df_clustered = create_development_clusters_without_analysis(df_edited, 4)

dims = [
        "Real_GDP_per_Capita_USD",
        "Life_Expectancy_at_Birth_(years)",
        "Total_Literacy_Rate [%]",
        "Expected_Years_of_Schooling_(years)",
        "Youth_Unemployment_Rate_percent",
    ]
