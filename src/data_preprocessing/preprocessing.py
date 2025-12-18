import pathlib
import pandas as pd
from thefuzz import process
import pycountry
from src.data_preprocessing.mappings import country_map
from src.data_preprocessing.regions import add_region_column
import re
import numpy as np
from dateutil.parser import parse
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



def load_external_data() -> dict[str, pd.DataFrame]:
    """
    Loads external data that we incorporated (so not the cia one) into a dict of DataFrames.

    @return DataFrame containing the data from the CSV file.
    """
    data_dict = dict()
    directory_path = pathlib.Path(__file__).parent.parent.parent/'external_data'
    for file in directory_path.glob('*.csv'):
        key = file.stem
        path_to_file = directory_path / file.name
        df = pd.read_csv(path_to_file)
        data_dict[key] = df

    return data_dict
        

#region Cleaning functions for specific datasets

#region helpers for cleaning geo data
def _dms_to_decimal(deg: float, minutes: float, hemi: str) -> float:
    """convert degrees + minutes + hemisphere to signed decimal degrees."""
    sign = -1 if hemi.upper() in ("S", "W") else 1
    return sign * (float(deg) + float(minutes) / 60.0)


def _parse_one_coord(token: str):
    """
    Parse a single coordinate like '34 00 N'
    Returns decimal degrees or pd.NA on failure
    """
    if pd.isna(token):
        return pd.NA

    bits = str(token).strip().replace("°", "").split()
    if len(bits) < 2:
        return pd.NA

    hemi = bits[-1].upper()
    nums = bits[:-1]

    try:
        if len(nums) == 2:
            deg, minutes = nums
        elif len(nums) == 1:
            deg, minutes = nums[0], 0
        else:
            #sometimes we might get deg, min, sec. just ignore sec?
            deg, minutes = nums[0], nums[1]

        return _dms_to_decimal(float(deg), float(minutes), hemi)
    except (ValueError, TypeError):
        return pd.NA


def _parse_geographic_coordinates(s: str):
    """
    Make '34 00 N, 62 00 E' to (lat_dd, lon_dd).
    Returns (pd.NA, pd.NA) on failure.
    """
    if pd.isna(s):
        return pd.NA, pd.NA

    parts = [p.strip() for p in str(s).split(",")]
    if len(parts) != 2:
        return pd.NA, pd.NA

    lat_token, lon_token = parts
    lat = _parse_one_coord(lat_token)
    lon = _parse_one_coord(lon_token)
    return lat, lon


def _parse_km_value(value):
    """
    Parse strings like '652,230 sq km', '5,987 km', '14.2 million sq km'
    into a numeric value in km or sq km (we don't know which; caller
    knows from context)
    """
    if pd.isna(value):
        return pd.NA

    s = str(value).strip().lower()
    if s in ("", "na", "n/a", "-", "none"):
        return pd.NA

    factor = 1.0
    if "million" in s:
        factor = 1_000_000.0

    #keep only digits, minus, and decimal point
    num_str = re.sub(r"[^0-9\.\-]", "", s)
    if num_str == "":
        return pd.NA

    try:
        return float(num_str) * factor
    except ValueError:
        return pd.NA


def _parse_percent_value(value):
    """
    Parse '12.3%' to 12.3
    """
    if pd.isna(value):
        return pd.NA

    s = str(value).strip()
    if s in ("", "na", "n/a", "-", "none"):
        return pd.NA

    s = s.replace("%", "").replace(",", "")
    try:
        return float(s)
    except ValueError:
        return pd.NA
#endregion

def clean_geography_data(geography_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the geography_data.csv df

    - split Geographic_Coordinates into numeric Latitude / Longitude
    - convert all 'sq km' and 'km' columns to numeric and append '_sq_km' / '_km' to names
    - convert all percentage columns to numeric and append '_%' to names.
    - not doing anything about missing values
    """
    df = geography_df.copy()

    # Geographic coordinates to Latitude / Longitude columns
    coord_col_candidates = [c for c in df.columns if "coord" in c.lower()]
    if coord_col_candidates:
        coord_col = coord_col_candidates[0]
        lats, lons = zip(*df[coord_col].apply(_parse_geographic_coordinates))
        df["Latitude"] = pd.to_numeric(pd.Series(lats), errors="coerce")
        df["Longitude"] = pd.to_numeric(pd.Series(lons), errors="coerce")
        # keep original coord column for reference mby?

    # Detect km / sq km / % columns and transform
    for col in list(df.columns):
        if not pd.api.types.is_object_dtype(df[col]):
            continue

        sample_values = df[col].dropna().astype(str).head(30).str.lower().tolist()
        sample_text = " ".join(sample_values)

        #% columns
        if "%" in sample_text:
            new_col_name = f"{col}_%"
            df[new_col_name] = df[col].apply(_parse_percent_value)
            df.drop(columns=[col], inplace=True)
            continue

        #sq km columns
        if "sq km" in sample_text:
            new_col_name = f"{col}_sq_km"
            df[new_col_name] = df[col].apply(_parse_km_value)
            df.drop(columns=[col], inplace=True)
            continue

        #km columns (not sq km)
        if " km" in sample_text or sample_text.endswith("km"):
            new_col_name = f"{col}_km"
            df[new_col_name] = df[col].apply(_parse_km_value)
            df.drop(columns=[col], inplace=True)
            continue

    return df

def clean_government_data(gov_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the government/political dataset minimally.
    Parse Capital_Coordinates into numeric Capital_Latitude and Capital_Longitude.
    """
    df = gov_df.copy()

    #parse coordinates (use geo helpers)
    coord_cols = [c for c in df.columns if "coord" in c.lower()]
    if coord_cols:
        coord_col = coord_cols[0]

        lats, lons = zip(*df[coord_col].apply(_parse_geographic_coordinates))
        df["Capital_Latitude"] = pd.to_numeric(pd.Series(lats), errors="coerce")
        df["Capital_Longitude"] = pd.to_numeric(pd.Series(lons), errors="coerce")

    return df

#region helpers for cleaning transportation data
def _parse_numeric(value):
    """
    Convert values like '58,000', '  1200 ', '-', '' to numeric or NaN.
    """
    if pd.isna(value):
        return np.nan
    
    s = str(value).strip().lower()
    if s in ("", "na", "n/a", "-", "none", "null"):
        return np.nan
    
    # Remove commas, spaces, and other non-numeric characters
    s = re.sub(r"[^0-9\.\-]", "", s)
    if s == "":
        return np.nan

    try:
        return float(s)
    except ValueError:
        return np.nan
#endregion

def clean_transportation_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean transportation_data.csv.
    - Convert all numeric columns to float
    - Replace missing numerical values with NaN
    """
    clean_df = df.copy()

    numeric_columns = [
        col for col in clean_df.columns 
        if col.lower() != "country"
    ]

    for col in numeric_columns:
        clean_df[col] = clean_df[col].apply(_parse_numeric)
        clean_df[col] = clean_df[col].astype("Float64")  #pandas nullable float

    return clean_df

def _fiscal_year_to_md(fy_string):
    """
    Converts 'calendar year' or 'day Month - day Month'
    to month-day strings like '01-01' and '12-31'.
    No full dates. No year.
    """
    if pd.isna(fy_string):
        return None, None

    fy_string = str(fy_string).strip().lower()

    if fy_string == "calendar year":
        return "01-01", "12-31"

    if "-" in fy_string:
        part1, part2 = fy_string.split("-")
        start_md = parse(part1.strip(), dayfirst=True)
        end_md   = parse(part2.strip(), dayfirst=True)

        start_str = f"{start_md.month:02d}-{start_md.day:02d}"
        end_str   = f"{end_md.month:02d}-{end_md.day:02d}"

        return start_str, end_str

    return None, None

#endregion

def clean_economy_data(df_economy:pd.DataFrame) -> pd.DataFrame:
    # If 'Fiscal_Year' is not present, assume data is already cleaned/processed
    if "Fiscal_Year" not in df_economy.columns:
        return df_economy

    df_economy["Fiscal_Year_Start_Date"], df_economy["Fiscal_Year_End_Date"] = zip(
    *df_economy["Fiscal_Year"].apply(_fiscal_year_to_md))

    df_economy = df_economy.drop(columns=['Fiscal_Year'])

    cols = list(df_economy.columns)

    # find index of Public_Debt_percent_of_GDP if present, otherwise append at end
    if "Public_Debt_percent_of_GDP" in cols:
        insert_at = cols.index("Public_Debt_percent_of_GDP") + 1
    else:
        insert_at = len(cols)

    # remove the new columns from the end
    cols.remove("Fiscal_Year_Start_Date")
    cols.remove("Fiscal_Year_End_Date")

    # insert them in correct order
    cols[insert_at:insert_at] = ["Fiscal_Year_Start_Date", "Fiscal_Year_End_Date"]

    # reorder dataframe
    df_economy = df_economy[cols]

    return df_economy


def clean_demographics_data(df_demographics: pd.DataFrame) -> pd.DataFrame:
    percent_cols = [
    'Population_Growth_Rate',
    'Total_Literacy_Rate',
    'Male_Literacy_Rate',
    'Female_Literacy_Rate',
    'Youth_Unemployment_Rate'
    ]

    # Removing '%' 
    for col in percent_cols:
        if col in df_demographics.columns:
            df_demographics[col] = (
                df_demographics[col]
                .astype(str)           
                .str.replace('%', '', regex=False)  
            )
            df_demographics[col] = pd.to_numeric(df_demographics[col], errors='coerce')

    rename_map = {col: f"{col} [%]" for col in percent_cols if col in df_demographics.columns}
    df_demographics = df_demographics.rename(columns=rename_map)

    return df_demographics

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
    
    df["Country"] = df["Country"].map(country_map).dropna()
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



""" data_dict = load_data()

#cleaned datasets
data_dict["geography_data"] = clean_geography_data(data_dict["geography_data"])
data_dict["government_and_civics_data"] = clean_government_data(data_dict["government_and_civics_data"])
data_dict["transportation_data"] = clean_transportation_data(data_dict["transportation_data"])
data_dict["demographics_data"] = clean_demographics_data(data_dict["demographics_data"])
data_dict["economy_data"] = clean_economy_data(data_dict["economy_data"])


merged_data = merge_data(data_dict)

 
merged_data = clean_country_names(merged_data)

# Add region column based on country
merged_data = add_region_column(merged_data)

for col in merged_data.columns:
    print(col, " - ", merged_data[col].dtype)


cols_to_ignore = ["Country", "ISO3"]  
mask = merged_data.drop(columns=cols_to_ignore).isna().all(axis=1)

only_nas = merged_data[mask] """
