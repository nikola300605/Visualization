import pathlib
import pandas as pd
from thefuzz import process
import pycountry
from src.data_preprocessing.mappings import country_map
# Manual mappings for country names that do not match pycountry entries

# Precompute list of country names for fuzzy matching
country_list = []
for c in pycountry.countries:
    country_list.append(c.name)

#Load all CSV files from the data directory into a dictionary of DataFrames
def load_data(directory_path =  pathlib.Path(__file__).parent.parent.parent/'data') -> dict[str, pd.DataFrame]:
    """
    Load all CSV files from the data directory into a dictionary of DataFrames.

    @param directory_path: Path to the directory containing CSV files.
    @return: Dictionary where keys are file names (without .csv) and values are Data
    """
    data_dict = {}
    # Read each CSV file and store in the dictionary
    for file in directory_path.glob('*.csv'):
        key = file.stem
        path_to_file = directory_path / file.name
        df = pd.read_csv(path_to_file)
        data_dict[key] = df



    return data_dict

def clean_and_format_economy_data(economy_df: pd.DataFrame) -> pd.DataFrame:
    pass

def merge_data(data_dict: dict[str, pd.DataFrame], key='Country') -> pd.DataFrame:
    """
    Merge multiple DataFrames in the data dictionary on a common key.

    @param data_dict: Dictionary of DataFrames to merge.
    @param key: Column name to merge on.
    @return: Merged DataFrame.
    """
    merged_df = None
    for df in data_dict.values():
        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on=key, how='outer')
    return merged_df

##### This is the parsing function we were asked for in assignment 1
def get_value(df, row, col):
    """
    Get a specific value from a DataFrame given row and column indices.
    @param df: DataFrame to extract value from.
    @param row: Row index.
    @param col: Column index.
    @return: Value at the specified row and column.
    """
    return df.iloc[row, col]

def get_ISO3(name: str, country_list: list=country_list) -> str | None:
    """
    Get the ISO3 country code for a given country name.
    Uses manual mappings and fuzzy matching for names not directly found.

    @param name: Country name to look up.
    @return: ISO3 country code or None if not found.
    """

    if pd.isna(name):
        return None
    
    name = str(name).strip()
    match, score = process.extractOne(name, country_list) 

    if score < 88:  # safer high threshold
        return None

    country = pycountry.countries.get(name=match)
    if country is None:
        return None

    return country.alpha_3



def clean_country_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and formats country names and adds ISO3 codes to the DataFrame.
    Deletes countries/territories that cannot be matched to ISO3 codes.
    Also adds countries which are not in the original data but have ISO3 codes (for map completness).

    @param df: DataFrame containing country names.
    @param column: Column name with country names to clean.
    @return: Tuple of DataFrames, where first is the full merged dataframe, and second is the dataframe with countries with no data.
    """
    
    df["Country"] = df["Country"].map(country_map).fillna(df["Country"])
    df["Country"] = df["Country"].astype(str).str.strip()

    df["Country"] = df["Country"].replace({
    "Gaza Strip": "Palestine, State of",
    "West Bank": "Palestine, State of"
    })
    agg_rules = {}

    for col in df.columns:
        if col == "Country":
            agg_rules[col] = "first"
        else:
            # Use numeric mean where possible
            if pd.api.types.is_numeric_dtype(df[col]):
                agg_rules[col] = "mean"  # or "sum" if you prefer
            else:
                agg_rules[col] = "first"

    # Group the dataset
    df = df.groupby("Country", as_index=False).agg(agg_rules)

    #Add missing countries with ISO3 codes but no data
    all_countries = list(set(country_list))  # deduplicate if you added official_name
    existing_countries = df["Country"].tolist()

    missing_countries = [c for c in all_countries if c not in existing_countries]

    missing_data = pd.DataFrame({"Country": missing_countries})
    df = pd.concat([df, missing_data], ignore_index=True)

    df['ISO3'] = df['Country'].apply(get_ISO3)

    return df

def analyse_distribution(df: pd.DataFrame):

    """
    Analyse the distribution of values in each column of the DataFrame.
    @param df: DataFrame to analyse.
    @return: Dictionary with column names as keys and distribution info as values.
    """

    results = {}
    for col in df.columns:
        series = df[col]

        if pd.api.types.is_numeric_dtype(series):
            stats = series.describe().to_dict()
            results[col] = {
                "type": 'numeric',
                "summary_stats": stats
            }
        else:
            counts = series.value_counts(dropna=False).to_dict()
            results[col] = {
                "type": "categorical",
                "value_counts": counts
            }
    return results





data_dict = load_data()
merged_data = merge_data(data_dict)

""" distribution_info = analyse_distribution(merged_data)
for type, info in distribution_info.items():
    print(f"{type}, \n {info}") """

merged_data = clean_country_names(merged_data)

cols_to_ignore = ["Country", "ISO3"]  
mask = merged_data.drop(columns=cols_to_ignore).isna().all(axis=1)

only_nas = merged_data[mask]

print(only_nas)


print(merged_data["Population_Growth_Rate"].nsmallest(10))