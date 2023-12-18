#dodaje 
import pandas as pd
import sqlite3

def del_unit(df):
    df['Rodzaj'] = df['Rodzaj'].str.replace(r'\[.*\]', '', regex=True)
    return df

def remove_spaces_from_column_names(df):
    df.columns = df.columns.str.strip()  # Remove leading and trailing spaces from column names
    df.columns = df.columns.str.replace(r'\s+', ' ', regex=True)  # Remove extra spaces within column names
    return df

def remove_spaces_from_data(df):
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df = df.applymap(lambda x: x if type(x) != str else ' '.join(x.split()))
    return df

def drop_columns_with_all_nan(df):
    df.dropna(axis=1, how='all', inplace=True)
    return df

def split_dataframe_to_list(df, column_name):
    unique_values = df[column_name].unique()
    dataframes_list = [df[df[column_name] == value].copy() for value in unique_values]
    return dataframes_list

def set_dataframe_names_from_rodzaj(dataframes_list):
    for df in dataframes_list:
        rodzaj_value = df['Rodzaj'].iloc[0] if not df.empty else ""
        df.name = rodzaj_value

def get_dataframe_by_name(dataframes_list, name):
    for df in dataframes_list:
        if hasattr(df, 'name') and df.name == name:
            return df
    return None


def handle_24_hour_time(value):
    if pd.isnull(value):  # Check if the value is NaN
        return value

    if '24:' in str(value):  # Convert value to string and check for '24:'
        date_part, time_part = str(value).split(' ')
        incremented_date = (pd.to_datetime(date_part) + pd.DateOffset(1)).strftime('%Y-%m-%d')
        return f"{incremented_date} {time_part.replace('24:', '00:')}"

    return value

def prepare_data(df):
    df = remove_spaces_from_column_names(df)
    df['Data'] = df['Data'].apply(handle_24_hour_time)  # Apply custom function to handle '24:00'
    df['Data'] = pd.to_datetime(df['Data'], format='%Y-%m-%d %H:%M')
    df = drop_columns_with_all_nan(df)
    
    # Extract unit information from 'Rodzaj' column and create a new 'Unit' column
    df['Unit'] = df['Rodzaj'].str.extract(r'\[(.*?)\]')[0].str.strip()
    df = del_unit(df)
    
    column_name = 'Rodzaj'
    resulting_dataframes = split_dataframe_to_list(df, column_name)
    set_dataframe_names_from_rodzaj(resulting_dataframes)
    
    # Reset index and convert 'Data' column to datetime for each dataframe
    for df_part in resulting_dataframes:
        df_part.reset_index(drop=True, inplace=True)
        df_part['Data'] = pd.to_datetime(df_part['Data'], format='%Y-%m-%d %H:%M')
    
    return resulting_dataframes

def create_table(cursor, table_name):
    # Create a table if it doesn't exist
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            Data TIMESTAMP PRIMARY KEY,
            -- Add other columns here based on your DataFrame structure
            -- For example, you might add columns like 'Value', 'Unit', etc.
            -- Adjust the data types accordingly
            Value FLOAT,
            Unit TEXT
        );
    ''')

def insert_data(cursor, table_name, df_part):
    # Insert data into the table, replacing existing records with the same primary key (Data)
    df_part.to_sql(table_name, conn, if_exists='append', index=False, index_label='Data')



csv_file_path = 'duze.csv'

# Read the CSV file into a Pandas DataFrame
df = pd.read_csv(csv_file_path, delimiter=';')
dataframes=prepare_data(df)


# Connect to SQLite database
conn = sqlite3.connect('baza.db')
cursor = conn.cursor()

# Iterate through dataframes and insert data into tables
for df_part in dataframes:
    table_name = df_part.name
    
    create_table(cursor, table_name)
    insert_data(cursor, table_name, df_part)

# Commit the changes and close the connection
conn.commit()
conn.close()