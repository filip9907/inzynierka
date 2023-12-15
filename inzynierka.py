#działa z kalendarzem i jest popap że daty nie prawidłowe

# libs
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkcalendar import DateEntry
from ttkthemes import ThemedStyle # Import ThemedStyle from ttktheme
from tkinter import messagebox 

# data process func

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
def select_csv_file():
    global dataframes_list_pobrana, pobrana
    global dataframes_list_oddana, oddana
    global dataframes_list_bierna_indukcyjna, bierna_indukcyjna
    global dataframes_list_bierna_pojemnosciowa, bierna_pojemnosciowa
    global dataframes_list_pobrana_po_zbilansowaniu, pobrana_po_zbilansowaniu
    global dataframes_list_oddana_po_zbilansowaniu, oddana_po_zbilansowaniu

    global min_date, max_date  # Add global min_date and max_date

    file_path = tk.filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV files", "*.csv")])
    if file_path:
        csv_file = file_path
        # Read the new CSV file into a Pandas DataFrame
        dane = pd.read_csv(csv_file, sep=';')

        # Update the data processing with the new CSV file
        dataframes_list_pobrana, pobrana = prepare_data(dane, "pobrana ")
        dataframes_list_oddana, oddana = prepare_data(dane, "oddana ")
        dataframes_list_bierna_indukcyjna, bierna_indukcyjna = prepare_data(dane, "bierna indukcyjna ")
        dataframes_list_bierna_pojemnosciowa, bierna_pojemnosciowa = prepare_data(dane, "bierna pojemnościowa ")
        dataframes_list_pobrana_po_zbilansowaniu, pobrana_po_zbilansowaniu = prepare_data(dane, "pobrana po zbilansowaniu ")
        dataframes_list_oddana_po_zbilansowaniu, oddana_po_zbilansowaniu = prepare_data(dane, "oddana po zbilansowaniu ")

        # Update the diagram
        update_diagram()

        # Update min_date and max_date
        min_date = dane['Data'].min()
        max_date = dane['Data'].max()

        # Update mindate and maxdate for DateEntry widgets
        start_date_entry.config(mindate=min_date, maxdate=max_date)
        end_date_entry.config(mindate=min_date, maxdate=max_date)

        print(f"Selected new CSV file: {csv_file}")
        return csv_file


# Replace 'your_file.csv' with the path to your CSV file
csv_file = 'duze.csv'

# Read the CSV file into a Pandas DataFrame
dane = pd.read_csv(csv_file, sep=';')

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


# now we have clear data
# Replace existing calls to prepare_data with the following
dataframes_list_pobrana, pobrana = prepare_data(dane, "pobrana ")
dataframes_list_oddana, oddana = prepare_data(dane, "oddana ")
dataframes_list_bierna_indukcyjna, bierna_indukcyjna = prepare_data(dane, "bierna indukcyjna ")
dataframes_list_bierna_pojemnosciowa, bierna_pojemnosciowa = prepare_data(dane, "bierna pojemnościowa ")
dataframes_list_pobrana_po_zbilansowaniu, pobrana_po_zbilansowaniu = prepare_data(dane, "pobrana po zbilansowaniu ")
dataframes_list_oddana_po_zbilansowaniu, oddana_po_zbilansowaniu = prepare_data(dane, "oddana po zbilansowaniu ")

def update_diagram():
    selected_values = diagram_listbox.curselection()

    if not selected_values:
        return  # No valid selection, do nothing

    selected_dataframes = [dataframes_list_pobrana[index] for index in selected_values]

    combined_dataframe = pd.concat(selected_dataframes)

    start_date = pd.Timestamp(start_date_entry.get_date())
    end_date = pd.Timestamp(end_date_entry.get_date())

    if end_date < start_date:
        messagebox.showerror("Error", "End Date cannot be earlier than Start Date")
        return  # Abort the function if end date is earlier than start date

    print(f"Start Date: {start_date}, End Date: {end_date}")

    print(f"Original DataFrame for {selected_values}:\n{combined_dataframe}")

    combined_dataframe = combined_dataframe[
        (combined_dataframe['Data'] >= start_date) & (combined_dataframe['Data'] <= end_date)
    ]

    print(f"Selected DataFrame for {selected_values} within the date range:\n{combined_dataframe}")

    ax.clear()
    for selected_dataframe in selected_dataframes:
        selected_dataframe_filtered = selected_dataframe[
            (selected_dataframe['Data'] >= start_date) & (selected_dataframe['Data'] <= end_date)
        ]
        ax.plot(selected_dataframe_filtered['Data'], selected_dataframe_filtered['Wartość'],
                label=selected_dataframe.name)

    ax.legend()
    ax.set_ylabel('Wartość [kWh]')
    ax.tick_params(axis='x', rotation=45)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    canvas.draw()

def save_diagram():
    file_path = tk.filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if file_path:
        fig.savefig(file_path, bbox_inches='tight')
        messagebox.showinfo("Save Diagram", f"Diagram saved successfully at:\n{file_path}")



# Find the minimum and maximum dates in your DataFrame
min_date = dane['Data'].min()
max_date = dane['Data'].max()
# Create the main application window
app = tk.Tk()
app.title("Diagram Viewer")

# Add a label above the listbox
select_power_label = tk.Label(app, text="Wybierz wyświetlaną moc:")
select_power_label.pack()

# Define the diagram_var before using it
diagram_var = tk.StringVar(app)

# Define diagram_options
diagram_options = ["pobrana", "oddana", "bierna_indukcyjna", "bierna_pojemnościowa", "pobrana_po_zbilansowaniu",
                   "oddana_po_zbilansowaniu"]

# Create the listbox with padding and expand
diagram_listbox = tk.Listbox(app, selectmode=tk.MULTIPLE, listvariable=diagram_var)
for option in diagram_options:
    diagram_listbox.insert(tk.END, option)
diagram_listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

# Separator for better visual separation
separator = ttk.Separator(app, orient="horizontal")
separator.pack(fill=tk.X, pady=5)

app = tk.Tk()
app.title("Diagram Viewer")

# Add a label above the listbox
select_power_label = tk.Label(app, text="Wybierz wyświetlaną moc:")
select_power_label.pack()

# Create the listbox with padding and expand
diagram_listbox = tk.Listbox(app, selectmode=tk.MULTIPLE, listvariable=diagram_var)
for option in diagram_options:
    diagram_listbox.insert(tk.END, option)
diagram_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

# Separator for better visual separation
separator = ttk.Separator(app, orient="horizontal")
separator.pack(side=tk.LEFT, fill=tk.Y, padx=5)

# Create DateEntry widgets for selecting start and end dates
start_date_label = tk.Label(app, text="Start Date:")
start_date_label.pack(side=tk.LEFT)
start_date_entry = DateEntry(app, date_pattern='yyyy-mm-dd', mindate=min_date, maxdate=max_date)
start_date_entry.pack(side=tk.LEFT, padx=5)

end_date_label = tk.Label(app, text="End Date:")
end_date_label.pack(side=tk.LEFT)
end_date_entry = DateEntry(app, date_pattern='yyyy-mm-dd', mindate=min_date, maxdate=max_date)
end_date_entry.pack(side=tk.LEFT, padx=5)

# Button to update and display the selected diagram
update_button = tk.Button(app, text="Update Diagram", command=update_diagram)
update_button.pack(side=tk.LEFT, pady=10, padx=5)

# Button to open a new window for selecting a CSV file
select_file_button = tk.Button(app, text="Select CSV File", command=select_csv_file)
select_file_button.pack(side=tk.LEFT, pady=10, padx=5)

save_button = tk.Button(app, text="Save Diagram", command=save_diagram)
save_button.pack(side=tk.LEFT, pady=10, padx=5)

# Matplotlib figure for displaying the diagram
fig = Figure(figsize=(8, 6), dpi=100)
ax = fig.add_subplot(111)
ax.set_facecolor('#f0f0f0')  # Set background color
ax.grid(True, linestyle='--', alpha=0.6)  # Add grid lines

canvas = FigureCanvasTkAgg(fig, master=app)
canvas.get_tk_widget().pack()


# Run the application
app.mainloop()
