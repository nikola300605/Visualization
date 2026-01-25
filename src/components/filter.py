import pandas as pd

# Comprehensive column label mapping for human-readable display
COLUMN_LABELS = {
    # Core identifiers
    "Country": "Country",
    "ISO3": "ISO3 Code",
    
    # Geographic data
    "Latitude": "Latitude",
    "Longitude": "Longitude",
    "Area_Total_sq_km": "Total Area (sq km)",
    "Area_Land_sq_km": "Land Area (sq km)",
    "Area_Water_sq_km": "Water Area (sq km)",
    "Coastline_km": "Coastline (km)",
    "Border_Countries": "Bordering Countries",
    "Terrain": "Terrain",
    "Climate": "Climate",
    "Natural_Hazards": "Natural Hazards",
    
    # Government/Capital data
    "Capital": "Capital",
    "Capital_Latitude": "Capital Latitude",
    "Capital_Longitude": "Capital Longitude",
    "Government_Type": "Government Type",
    "Head_of_State": "Head of State",
    "Head_of_Government": "Head of Government",
    
    # Population & Demographics
    "Total_Population": "Total Population",
    "Population_Growth_Rate_(percentage)": "Population Growth Rate (%)",
    "Median_Age": "Median Age",
    "Birth_Rate": "Birth Rate",
    "Death_Rate": "Death Rate",
    "Total_Fertility_Rate": "Total Fertility Rate",
    "Infant_Mortality_Rate": "Infant Mortality Rate",
    "Life_Expectancy_at_Birth_(years)": "Life Expectancy at Birth (years)",
    
    # Literacy & Education
    "Total_Literacy_Rate [%]": "Literacy Rate (%)",
    "Male_Literacy_Rate [%]": "Male Literacy Rate (%)",
    "Female_Literacy_Rate [%]": "Female Literacy Rate (%)",
    "Expected_Years_of_Schooling_(years)": "Expected Years of Schooling",
    "Adolescent_Birth_Rate_(births_per_1,000_women_ages_15-19)": "Adolescent Birth Rate",
    
    # Economic data
    "Real_GDP_per_Capita_USD": "Real GDP per Capita (USD)",
    "Real_GDP_PPP_billion_USD": "Real GDP PPP (billion USD)",
    "GDP_Official_Exchange_Rate_billion_USD": "GDP at Official Rate (billion USD)",
    "Real_GDP_Growth_Rate_percent": "Real GDP Growth Rate (%)",
    "Public_Debt_percent_of_GDP": "Public Debt (% of GDP)",
    "Budget_billion_USD": "Budget (billion USD)",
    "Budget_Deficit_percent_of_GDP": "Budget Deficit (% of GDP)",
    "Exports_billion_USD": "Exports (billion USD)",
    "Imports_billion_USD": "Imports (billion USD)",
    "Trade_Balance_billion_USD": "Trade Balance (billion USD)",
    "Exchange_Rate_per_USD": "Exchange Rate (per USD)",
    "Unemployment_Rate_percent": "Unemployment Rate (%)",
    "Youth_Unemployment_Rate_percent": "Youth Unemployment Rate (%)",
    "Population_Below_Poverty_Line_percent": "Population Below Poverty Line (%)",
    
    # Human Development Index
    "Human_Development_Index_(value)": "Human Development Index",
    "Inequality-adjusted_Human_Development_Index_(value)": "Inequality-Adjusted HDI",
    
    # Infrastructure & Transportation
    "roadways_km": "Roadways (km)",
    "railroads_km": "Railroads (km)",
    "waterways_km": "Waterways (km)",
    "Airports": "Airports",
    "Merchant_Fleet_Ships": "Merchant Fleet Ships",
    "road_density": "Road Density",
    "road_density_log": "Road Density (log scale)",
    
    # Communications & Technology
    "internet_users_total": "Internet Users (total)",
    "internet_penetration_rate": "Internet Penetration Rate (%)",
    "broadband_fixed_subscriptions_total": "Broadband Subscriptions (total)",
    "broadband_fixed_subscriptions_rate": "Broadband Subscriptions Rate (%)",
    "Telephone_Lines": "Telephone Lines",
    "Mobile_Cellular_Subscriptions": "Mobile Cellular Subscriptions",
    
    # Energy & Resources
    "Electricity_Production_billion_kWh": "Electricity Production (billion kWh)",
    "Electricity_Consumption_billion_kWh": "Electricity Consumption (billion kWh)",
    "electricity_access_percent": "Electricity Access (%)",
    "Oil_Production_barrels_per_day": "Oil Production (barrels/day)",
    "Oil_Consumption_barrels_per_day": "Oil Consumption (barrels/day)",
    "Natural_Gas_Production_billion_cu_m": "Natural Gas Production (billion cu m)",
    "Natural_Gas_Consumption_billion_cu_m": "Natural Gas Consumption (billion cu m)",
    
    # Land & Agriculture
    "Agricultural_Land_%": "Agricultural Land (%)",
    "Arable_Land (%% of Total Agricultural Land)_%": "Arable Land (% of Agricultural)",
    "Permanent_Crops_%": "Permanent Crops (%)",
    "Irrigated_Land_sq_km": "Irrigated Land (sq km)",
    "irrigated_land_percent": "Irrigated Land (%)",
    "population_density": "Population Density",
    
    # Migration
    "Net_Migration_Rate_(per_1,000_population)": "Net Migration Rate (per 1,000)",
    
    # Fiscal year info
    "Fiscal_Year_Start_Date": "Fiscal Year Start",
    "Fiscal_Year_End_Date": "Fiscal Year End",
}


def get_label(col_name: str) -> str:
    """
    Get human-readable label for a column name.
    Falls back to title-cased column name if not in mapping.
    
    @param col_name: Column name from dataframe
    @return: Human-readable label
    """
    if col_name in COLUMN_LABELS:
        return COLUMN_LABELS[col_name]
    
    # Fallback: title case and replace underscores with spaces
    return col_name.replace("_", " ").replace(" [%]", "").title()


def filter_df(df: pd.DataFrame, active_filters: dict, default_filters: dict) -> tuple[pd.DataFrame, dict, dict]:
    if not active_filters:
        return df, {}, {}
    
    mask = pd.Series([True] * len(df), index=df.index)


    active_filter_dict = {}
    missing_by_filter = {}

    for col, val in active_filters.items():

        if col not in df.columns or val is None or col is None:
            continue

        is_active = val != default_filters.get(col, None)

        if isinstance(val, list):
            low, high = val
            if is_active:
                active_filter_dict[col] = val
                missing_by_filter[col] = set(df[df[col].isna()]["ISO3"].tolist())

                cond = (df[col] >= low) & (df[col] <= high)
            else:
                cond = df[col].isna() | ((df[col] >= low) & (df[col] <= high))

        else:
            if is_active:
                active_filter_dict[col] = val
                missing_by_filter[col] = set(df[df[col].isna()]["ISO3"].tolist())
                cond = (df[col] >= val)
            else:
                cond = df[col].isna() | (df[col] >= val)

        mask &= cond

    return df[mask], active_filter_dict, missing_by_filter