import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkcalendar import DateEntry
from ttkthemes import ThemedStyle # Import ThemedStyle from ttktheme
from tkinter import messagebox 
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

# Data processing




def handle_24_hour_time(value):
    if pd.isnull(value):  # Check if the value is NaN
        return value

    if '24:' in str(value):  # Convert value to string and check for '24:'
        date_part, time_part = str(value).split(' ')
        incremented_date = (pd.to_datetime(date_part) + pd.DateOffset(1)).strftime('%Y-%m-%d')
        return f"{incremented_date} {time_part.replace('24:', '00:')}"

    return value


def prepare_data(df, rodzaj):
    df = remove_spaces_from_column_names(df)
    df['Data'] = df['Data'].apply(handle_24_hour_time)  # Apply custom function to handle '24:00'
    df['Data'] = pd.to_datetime(df['Data'], format='%Y-%m-%d %H:%M')
    df = drop_columns_with_all_nan(df)
    df = del_unit(df)
    column_name = 'Rodzaj'
    resulting_dataframes = split_dataframe_to_list(df, column_name)
    set_dataframe_names_from_rodzaj(resulting_dataframes)
    selected_dataframe = get_dataframe_by_name(resulting_dataframes, rodzaj)
    selected_dataframe.reset_index(drop=True, inplace=True)
    selected_dataframe = selected_dataframe.iloc[:, :-1]
    selected_dataframe['Data'] = pd.to_datetime(selected_dataframe['Data'], format='%Y-%m-%d %H:%M')
    return resulting_dataframes, selected_dataframe
