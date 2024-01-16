import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import requests
from requests import adapters
import ssl
from urllib3 import poolmanager
from urllib.parse import urlencode
from io import StringIO
import csv
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

def create_table(cursor, table_name, df_part):
    # Extract column names from the DataFrame
    columns = list(df_part.columns)

    # Generate the CREATE TABLE statement dynamically
    create_table_statement = f'''
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            {", ".join(f'"{col}" {df_part[col].dtype}' for col in columns)},
            PRIMARY KEY ("Data")
        );
    '''

    # Execute the CREATE TABLE statement
    cursor.execute(create_table_statement)


def insert_data(cursor, table_name, df_part, conn):
    # Insert data into the table, replacing existing records with the same primary key (Data)
    df_part.to_sql(table_name, conn, if_exists='append', index=False, index_label='Data')


def fetch_data():
    start_date = start_date_entry.get_date().strftime('%Y-%m-%d')
    end_date = end_date_entry.get_date().strftime('%Y-%m-%d')
    username = username_entry.get()
    password = password_entry.get()
    meter_id = meter_id_entry.get()

    payload = { 
        'username': username,
        'password': password,
        'service': 'https://elicznik.tauron-dystrybucja.pl'
    }

    url = 'https://logowanie.tauron-dystrybucja.pl/login'
    charturl = 'https://elicznik.tauron-dystrybucja.pl/energia/wo/dane'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'} 

    class TLSAdapter(adapters.HTTPAdapter):

        def init_poolmanager(self, connections, maxsize, block=False):
            ctx = ssl.create_default_context()
            ctx.set_ciphers('DEFAULT@SECLEVEL=1')
            self.poolmanager = poolmanager.PoolManager(
                    num_pools=connections,
                    maxsize=maxsize,
                    block=block,
                    ssl_version=ssl.PROTOCOL_TLS,
                    ssl_context=ctx)

    session = requests.session()
    session.mount('https://', TLSAdapter())

    p = session.request("POST", url, data=payload, headers=headers)
    p = session.request("POST", url, data=payload, headers=headers)

    chart = {
        "form[from]": start_date,
        "form[to]": end_date,
        "form[type]": "15min",
        "form[energy][]": ["1", "2", "3", "6", "2001", "2002"],
        "form[fileType]": "CSV"
    }

    encoded_params = urlencode(chart, doseq=True)
    url_with_params = f"{charturl}?{encoded_params}"

    r = session.request("POST", url_with_params)

    if r.status_code == 200:
        content_string = r.content.decode('utf-8')
        print(content_string)  # Add this line to print the content
        try:
            df = pd.read_csv(StringIO(content_string), delimiter=';')
            dataframes = prepare_data(df)

            conn = sqlite3.connect('baza.db')
            cursor = conn.cursor()

            try:
                for df_part in dataframes:
                    table_name = df_part.name
                    create_table(cursor, table_name, df_part)
                    insert_data(cursor, table_name, df_part, conn)

                conn.commit()

            except Exception as e:
                print(f"Error during database operations: {e}")

            finally:
                conn.close()

        except pd.errors.ParserError as pe:
            print(f"Error parsing CSV data: {pe}")

    else:
        print(f"Error: {r.status_code}")

# Create the main window
root = tk.Tk()
root.title("Data Retrieval GUI")

# Create and place widgets
start_date_label = ttk.Label(root, text="Start Date:")
start_date_label.grid(row=0, column=0, padx=10, pady=10)

start_date_entry = DateEntry(root, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
start_date_entry.grid(row=0, column=1, padx=10, pady=10)

end_date_label = ttk.Label(root, text="End Date:")
end_date_label.grid(row=1, column=0, padx=10, pady=10)

end_date_entry = DateEntry(root, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
end_date_entry.grid(row=1, column=1, padx=10, pady=10)

username_label = ttk.Label(root, text="Username:")
username_label.grid(row=2, column=0, padx=10, pady=10)

username_entry = ttk.Entry(root)
username_entry.grid(row=2, column=1, padx=10, pady=10)

password_label = ttk.Label(root, text="Password:")
password_label.grid(row=3, column=0, padx=10, pady=10)

password_entry = ttk.Entry(root, show="*")
password_entry.grid(row=3, column=1, padx=10, pady=10)

meter_id_label = ttk.Label(root, text="Meter ID:")
meter_id_label.grid(row=4, column=0, padx=10, pady=10)

meter_id_entry = ttk.Entry(root)
meter_id_entry.grid(row=4, column=1, padx=10, pady=10)

fetch_button = ttk.Button(root, text="Fetch Data", command=fetch_data)
fetch_button.grid(row=5, column=0, columnspan=2, pady=20)

# Start the GUI main loop
root.mainloop()