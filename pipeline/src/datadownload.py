# %% tags=["parameters"]
# declare a list tasks whose products you want to use as inputs
upstream = None


# %%
# AUTOGENERATED! DO NOT EDIT! File to edit: datadownload.ipynb.

# %% auto 0
__all__ = ['model_dict', 'transmission_dict', 'fuel_dict', 'extract_metadata', 'extract_raw_data', 'merge_top_two_rows',
           'rename_columns', 'clean_content', 'init_duckdb', 'create_duckdb_table']

# %% datadownload.ipynb 1
from pathlib import Path
import requests
import csv
from io import StringIO
import pandas as pd
import json
import duckdb

# %% datadownload.ipynb 3
def extract_metadata(metadata_url):
    """
    Extracts a list of filenames and urls from Open Cananda metadata url.

    Parameters
    ----------
    metadata_url : str
        Fuel consumption ratings metadata url from Open Canada website.

    Returns
    -------
    english_resources_df : pd.DataFrame
        DataFrame of file names and urls for energy consumption ratings.
    """
    try:      
        metadata_resp = requests.get(metadata_url)
    except requests.exceptions.RequestException as e:
        # If request fails, return an error message and stop.
        print(f'Error making url request: {e}')
    
    try:     
        metadata_json = metadata_resp.json()
    except json.JSONDecodeError:
        # If parsing json fails, return an error message and stop.
        print(f'Error: Response is not valid json')
        
    # Access list of downloadable resources
    resources_df = pd.DataFrame(metadata_json['result']['resources'])

    # Change language coding and extract English only resources
    resources_df['language'] = resources_df['language'].apply(lambda item : item[0])
    english_resources_df = resources_df[resources_df['language'] == 'en']
    
    return english_resources_df[['name', 'url']]

# %% datadownload.ipynb 4
def extract_raw_data(url, file_name):
    """
    Extract raw data from a URL

    Parameters
    ----------
    url : str
        URL to extract data from
        
    file_name : str or Path object
        file name for raw data dump
        
    """
    
    try:
        # Request data from url
        response = requests.get(url)
        content_type = response.headers['content-type']
        response_text = response.text
        print(f'Response status: {response.status_code}\nContent Type: {content_type}')

        # Save request content to csv file
        with open(file_name, mode='w', newline='') as csvfile:
            csvfile.write(response_text)

        print(f'csv file: {file_name} saved')
        
    # Catch errors    
    except requests.exceptions.HTTPError as err_h:
        print(f'HTTP error occured:{err_h}')
    except requests.exceptions.ConnectionError as err_c:
        print(f'Error connecting:{err_c}')
    except requests.exceptions.Timeout as err_t:
        print(f'Timeout Error:{err_t}')
    except requests.exceptions.RequestException as err:
        print(f'There was an unknown error:{err}')

# %% datadownload.ipynb 5
def merge_top_two_rows(input_file, output_file):
    # Open the input CSV file for reading
    with open(input_file, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        
        # Read the first two rows from the input file
        header_row = next(reader)
        second_row = next(reader)
        
        # Merge the two rows into one header
        merged_header = [f"{header_row[i]} {second_row[i]}" for i in range(len(header_row))]
        
        # Open the output CSV file for writing
        with open(output_file, mode='w', newline='') as output_csvfile:
            writer = csv.writer(output_csvfile)
            
            # Write the merged header to the output file
            writer.writerow(merged_header)
            
            # Copy the rest of the rows from the input file to the output file
            for row in reader:
                writer.writerow(row)

# %% datadownload.ipynb 6
def rename_columns(df):
    """
    Removes unwanted DataFrame columns and rows, then cleans and renames column headers.

    Parameters
    ----------
    df: DataFrame
        DataFrame with columns to clean

    Returns
    -------
    df: DataFrame
        DataFrame with cleaned column headers

    """
    # Drop empty columns and rows from the DataFrame
    df.dropna(axis=1, how='all', inplace=True)
    df.dropna(axis=0, thresh=5, inplace=True)

    # Remove whitespace, replace spaces with _ and change to lower case
    cleaned_cols = (df.columns.str.lower()
                    .str.strip()
                    .str.replace(' # = high output engine', '')
                    .str.replace('*', '')
                    .str.replace('  ', ' ')
                    .str.replace(' ', '_')
                    .str.replace('(', '')
                    .str.replace(')', '')
                    .str.replace('/', '_')
                    .str.replace('fuel_consumption_', '')
                    .str.replace('consumption_', '')
                    .str.replace('_le_', '_l_')
                    .str.replace('city_l_100_km', 'consumption_city_l_100_km')
                    .str.replace('comb_l_100_km', 'consumption_comb_l_100_km')
                    .str.replace('hwy_l_100_km', 'consumption_hwy_l_100_km')
    )

    col_mapper = dict(list(zip(df.columns, cleaned_cols))) # build a dictionary to map old column names to new
    df.rename(columns=col_mapper, inplace=True)

    return df  

# %% datadownload.ipynb 7
def clean_content(df):
    """
    Clean content of master_df columns

    Parameters
    ----------
    df : DataFrame
        Should be master_df containing all fuel rating data combined
    """
    
    # Set fuel type columns using fuel_dict
    df['fuel_type'] = df['fuel_type'].map(fuel_dict)
    df['fuel_type_1'] = df['fuel_type_1'].map(fuel_dict)
    df['fuel_type_2'] = df['fuel_type_2'].map(fuel_dict)

    # Set make, model and vehicle_class to lower case and remove ":" characters
    df['make'] = df['make'].str.lower().str.strip()
    df['model'] = df['model'].str.lower().str.strip()
    df['vehicle_class'] = df['vehicle_class'].str.lower().str.strip()
    df['vehicle_class'] = df['vehicle_class'].str.replace(":", "-")

    # Set make, model and vehicle_class to category columns
    df['make'] = df['make'].astype('category')
    df['model'] = df['model'].astype('category')
    df['vehicle_class'] = df['vehicle_class'].astype('category')

    # Split transmission column into transmission type and number of gears
    df = df.join(df['transmission'].str.split(r"(\d+)", expand=True)
                          .drop(columns=[2])
                          .rename(columns={0: 'transmission_type', 1: 'number_of_gears'})
    )

    df['transmission_type'] = df['transmission_type'].map(transmission_dict)
    df.drop(columns='transmission', inplace=True)

    df.reset_index()
    df['id'] = df.index

    return df

# %% datadownload.ipynb 8
def init_duckdb(db_file_path, tables):
    """
    Initialize a DuckDB data base and create tables for each DataFrame

    Parameters
    ----------
    db_file_path : str
        Path to the DuckDB database file
    tables : list
        Dictionary of table names and references to DataFrames for those tables 
    """
    db_connection = duckdb.connect(db_file_path)
    for key, value in tables.items():
        create_duckdb_table(db_connection, key, value)

# %% datadownload.ipynb 9
def create_duckdb_table(db_connection, table_name, df):
    """
    Create a table in DuckDB

    Parameters
    ----------
    db_connection : duckdb.conect
        Connection to DuckDB
    table_name : str
        Name of the table to be created
    df : str
        Nmae of the DataFrame to be used to create the table.
    """
    db_connection.execute(f"DROP TABLE IF EXISTS {table_name}")
    db_connection.execute(f"CREATE TABLE {table_name} AS SELECT * FROM {df}")

# %% datadownload.ipynb 10
global model_dict
global transmission_dict
global fuel_dict

model_dict = {
    "4wd/4X4": "Four-wheel drive",
    "awd": "All-wheel drive",
    "ffv": "Flexible-fuel vehicle",
    "swb": "Short wheelbase",
    "lwb": "Long wheelbase",
    "ewb": "Extended wheelbase",
    "cng": "Compressed natural gas",
    "ngv": "Natural gas vehicle",
    "#": "High output engine that \
            provides more power than the standard \
            engine of the same size",
}

transmission_dict = {
    "A": "automatic",
    "AM": "automated manual",
    "AS": "automatic with select Shift",
    "AV": "continuously variable",
    "M": "manual",
}

fuel_dict = {
    "X": "regular gasoline",
    "Z": "premium gasoline",
    "D": "diesel",
    "E": "ethanol (E85)",
    "N": "natural gas",
    "B": "electricity",
    "B/X": "electricity & regular gasoline",
    "B/Z": "electricity & premium gasoline",
    "B/Z*": "electricity & premium gasoline",
    "B/X*": "electricity & regular gasoline",
    "B": "electricity",
}

# %% datadownload.ipynb 11
if __name__ == "__main__":
    url = 'https://natural-resources.canada.ca/sites/nrcan/files/oee/files/csv/MY2023%20Fuel%20Consumption%20Ratings.csv'
    metadata_url = 'https://open.canada.ca/data/api/action/package_show?id=98f1a129-f628-4ce4-b24d-6f16bf24dd64'
    
    # Build list of available resources
    resources_df = extract_metadata(metadata_url)
    
    # Remove unwanted old resources
    resources_df = resources_df[~resources_df['name'].str.contains('Original')]
    
    # Build filenames for desired resources and add to resources_df
    file_names = (resources_df['name']
         .str.replace(' ', '_')
         .str.replace('(', 'v_')
         .str.replace(')', '')
         .str.lower()
    )
    resources_df.loc[:,'file_name'] = file_names
    
    # Build raw data file path
    path = Path.cwd()
    raw_path = path / 'pipeline' / 'data' / 'raw'
    merged_header_path = path / 'pipeline' / 'data' / 'merged-headers'
    
    # Download and save raw data for each resource
    for idx, row in resources_df.iterrows():
        url = row.iloc[1]
        file_name = row.iloc[2]
        raw_file_name = raw_path / f'{file_name}.csv'
        merged_header_file_name = merged_header_path / f'{file_name}.csv'
        extract_raw_data(url, raw_file_name)
        merge_top_two_rows(raw_file_name, merged_header_file_name)
    
    # Start a list of column headers and initiate a master_df
    union_of_headers = set()
    master_df = pd.DataFrame()
    
    # Build the master DataFrame
    for idx, row in resources_df.iterrows():
        # Open each csv file
        url = row.iloc[1]
        file_name = row.iloc[2]
        merged_header_file_name = merged_header_path / f'{file_name}.csv'
    
        # Rename the columns
        df = pd.read_csv(merged_header_file_name)
        df = rename_columns(df)
    
        # Add vehicle type based on file_name
        if 'hybrid' in file_name:
            df['vehicle_type'] = 'hybrid'
        elif 'electric' in file_name and 'hybrid' not in file_name:
            df['vehicle_type'] = 'electric'
        else:
            df['vehicle_type'] = 'fuel-only'
            
        # Add any missing column headers to master DataFrame columns
        union_of_headers = set.union(union_of_headers, set(df.columns))
        missing_cols = set(master_df.columns) - union_of_headers
        if len(missing_cols) > 0:
            for col in missing_cols:
                master_df[col] = pd.Series()
            
        # Concatenate current df with master_df
        master_df = pd.concat([master_df, df], ignore_index=True)
        
    # Clean the master_df
    master_df = clean_content(master_df)
    
    # Create separate fuel, electric, and hybrid DataFrames
    electric_df = master_df.loc[master_df['vehicle_type'] == 'electric'].dropna(axis=1, how='all').reset_index()
    hybrid_df = master_df.loc[master_df['vehicle_type'] == 'hybrid'].dropna(axis=1, how='all').reset_index()
    fuel_df = master_df.loc[master_df['vehicle_type'] == 'fuel-only'].dropna(axis=1, how='all').reset_index()
    
    # Create dictionary to pass to init database
    tables = {'all_vehicles' : 'master_df', 'electric' : 'electric_df', 'hybrid' : 'hybrid_df', 'fuel' : 'fuel_df'}
    
    # Create directory for DuckDB database 
    db_path = path / 'pipeline' / 'data' / 'database'
    Path(db_path).mkdir(parents=True, exist_ok=True)
    # Create file path for DuckDB database
    db_file_path = str(db_path / 'car_data.duckdb')

    # Create DuckDB database
    init_duckdb(db_file_path, tables)

    print(f'Data downloaded and saved in DuckDB database: {db_file_path}')
