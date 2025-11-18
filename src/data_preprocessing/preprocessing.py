import pathlib
import pandas as pd

#Load all CSV files from the data directory into a dictionary of DataFrames
def load_data(directory_path):
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


def merge_data(data_dict, key='Country'):
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

def analyse_distribution(df):

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




csv_path = pathlib.Path(__file__).parent.parent.parent/'data'
data_dict = load_data(csv_path)
merged_data = merge_data(data_dict)

distribution_info = analyse_distribution(merged_data)
""" for type, info in distribution_info.items():
    print(f"{type}, \n {info}") """

print(merged_data.shape)


