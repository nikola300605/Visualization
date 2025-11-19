import pathlib
import pandas as pd
from thefuzz import process
import pycountry

# Manual mappings for country names that do not match pycountry entries
manual_iso3 = {
    "BAHAMAS, THE": "BHS",
    "BOLIVIA": "BOL",
    "BRUNEI": "BRN",
    "BURMA": "MMR",  # Myanmar

    "CONGO, DEMOCRATIC REPUBLIC OF THE": "COD",
    "CONGO, REPUBLIC OF THE": "COG",

    "CURACAO": "CUW",
    "FALKLAND ISLANDS (ISLAS MALVINAS)": "FLK",
    "FRENCH SOUTHERN AND ANTARCTIC LANDS": "ATF",

    "GAMBIA, THE": "GMB",
    "GAZA STRIP": "PSE",  # State of Palestine
    "HOLY SEE (VATICAN CITY)": "VAT",
    "IRAN": "IRN",

    "JAN MAYEN": "SJM",   # combined with Svalbard (SJM)
    "KOREA, NORTH": "PRK",
    "KOREA, SOUTH": "KOR",
    "KOSOVO": "XKX",      # not official ISO, but widely used

    "LAOS": "LAO",
    "MACAU": "MAC",
    "MOLDOVA": "MDA",
    "PITCAIRN ISLANDS": "PCN",
    "RUSSIA": "RUS",

    "SAINT BARTHELEMY": "BLM",
    "SAINT HELENA, ASCENSION, AND TRISTAN DA CUNHA": "SHN",
    "SAINT MARTIN": "MAF",
    "SINT MAARTEN": "SXM",

    "SOUTH GEORGIA AND SOUTH SANDWICH ISLANDS": "SGS",
    "SVALBARD": "SJM",  # combined with Jan Mayen (SJM)
    "SYRIA": "SYR",
    "TAIWAN": "TWN",
    "TANZANIA": "TZA",
    "TURKEY (TURKIYE)": "TUR",

    "VENEZUELA": "VEN",
    "VIETNAM": "VNM",
    "VIRGIN ISLANDS": "VIR",  # U.S. Virgin Islands
    "WEST BANK": "PSE",
}

# Precompute list of country names for fuzzy matching
country_list = [country.name for country in pycountry.countries]

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

def get_ISO3(name: str, manual_iso3: dict=manual_iso3, country_list: list=country_list) -> str | None:
    """
    Get the ISO3 country code for a given country name.
    Uses manual mappings and fuzzy matching for names not directly found.

    @param name: Country name to look up.
    @return: ISO3 country code or None if not found.
    """

    if pd.isna(name):
        return None
    
    if name in manual_iso3:
        return manual_iso3[name]
    
    # Try direct pycountry lookup (handles many aliases / codes)
    try:
        country = pycountry.countries.lookup(str(name).strip())
        return getattr(country, "alpha_3", None)
    except (LookupError, KeyError):
        pass

    match, score = process.extractOne(name, country_list)
    if score > 80:
        return pycountry.countries.get(name=match).alpha_3
    else:
        return None



def clean_country_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and formats country names and adds ISO3 codes to the DataFrame.
    Deletes countries/territories that cannot be matched to ISO3 codes.
    Also adds countries which are not in the original data but have ISO3 codes (for map completness).

    @param df: DataFrame containing country names.
    @param column: Column name with country names to clean.
    @return: DataFrame with cleaned country names.
    """
    df['ISO3'] = df['Country'].apply(get_ISO3)

    df['Country'] = df['Country'].str.strip().str.title()

    existing = set(df["Country"].str.strip().str.upper())
    iso_countries = {c.name.upper(): c.alpha_3 for c in pycountry.countries}

    missing = [name for name in iso_countries.keys() if name not in existing]
    missing_rows = pd.DataFrame({
        "Country": missing,
        "ISO3": [iso_countries[name] for name in missing]
    })

    for col in df.columns:
        if col not in missing_rows.columns:
            missing_rows[col] = pd.NA
    
    df = pd.concat([df, missing_rows], ignore_index=True)

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



print(merged_data.head())


