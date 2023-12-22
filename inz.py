import pandas as pd
import sqlite3

def import_tables_from_database(database_path):
    # Connect to SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Get the list of table names in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = cursor.fetchall()

    # Initialize an empty list to store DataFrames
    dataframes_list = []

    # Iterate through table names and import each table into a DataFrame
    for table_name in table_names:
        table_name = table_name[0]
        query = f'SELECT * FROM "{table_name}" ORDER BY Data ASC;'  # Enclose table name with spaces in double quotes
        df = pd.read_sql_query(query, conn)
        dataframes_list.append(df)

    # Close the connection
    conn.close()

    return dataframes_list

# Call the function to import all tables into a list of DataFrames
imported_dataframes = import_tables_from_database('baza.db')

dataframes_list_pobrana=imported_dataframes[0]
dataframes_list_oddana=imported_dataframes[1]
dataframes_list_bierna_indukcyjna=imported_dataframes[2]
dataframes_list_bierna_pojemnosciowa=imported_dataframes[3]
dataframes_list_pobrana_po_zbilansowaniu=imported_dataframes[4]
dataframes_list_oddana_po_zbilansowaniu=imported_dataframes[5]

print("Dataframes List Pobrana:")
print(dataframes_list_pobrana)

print("\nDataframes List Oddana:")
print(dataframes_list_oddana)

print("\nDataframes List Bierna Indukcyjna:")
print(dataframes_list_bierna_indukcyjna)

print("\nDataframes List Bierna Pojemnosciowa:")
print(dataframes_list_bierna_pojemnosciowa)

print("\nDataframes List Pobrana Po Zbilansowaniu:")
print(dataframes_list_pobrana_po_zbilansowaniu)

print("\nDataframes List Oddana Po Zbilansowaniu:")
print(dataframes_list_oddana_po_zbilansowaniu)
