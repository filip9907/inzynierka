#działa z kalendarzem i jest popap że daty nie prawidłowe

# libs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkcalendar import DateEntry
from ttkthemes import ThemedStyle # Import ThemedStyle from ttktheme
from tkinter import messagebox 
import sqlite3
# data process func


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
        df = df.drop_duplicates()
        df['Data']=pd.to_datetime(df['Data'])
        df['Wartość'] = df['Wartość'].str.replace(',', '.').astype(float)
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
dataframes_dict = {
    "pobrana": dataframes_list_pobrana,
    "oddana": dataframes_list_oddana,
    "bierna_indukcyjna": dataframes_list_bierna_indukcyjna,
    "bierna_pojemnosciowa": dataframes_list_bierna_pojemnosciowa,
    "pobrana_po_zbilansowaniu": dataframes_list_pobrana_po_zbilansowaniu,
    "oddana_po_zbilansowaniu": dataframes_list_oddana_po_zbilansowaniu,
}

min_date = dataframes_list_pobrana['Data'].min().date()
max_date = dataframes_list_pobrana['Data'].max().date()


# Create the main application window
app = tk.Tk()
app.title("Diagram Viewer")

# Add a label above the listbox
select_power_label = tk.Label(app, text="Wybierz wyświetlaną moc:")
select_power_label.pack()

# Define the diagram_var before using it
diagram_var = tk.StringVar(app)

# Define diagram_options
diagram_options = ["pobrana", "oddana", "bierna_indukcyjna", "bierna_pojemnosciowa", "pobrana_po_zbilansowaniu",
                   "oddana_po_zbilansowaniu"]

# Create the listbox with padding and expand
diagram_listbox = tk.Listbox(app, selectmode=tk.MULTIPLE, listvariable=diagram_var)
for option in diagram_options:
    diagram_listbox.insert(tk.END, option)
diagram_listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

# Separator for better visual separation
separator = ttk.Separator(app, orient="horizontal")
separator.pack(fill=tk.X, pady=5)

# Create DateEntry widgets for selecting start and end dates
start_date_label = tk.Label(app, text="Start Date:")
start_date_label.pack()
start_date_entry = DateEntry(app, date_pattern='yyyy-mm-dd', mindate=min_date, maxdate=max_date)
start_date_entry.pack(pady=5)

end_date_label = tk.Label(app, text="End Date:")
end_date_label.pack()
end_date_entry = DateEntry(app, date_pattern='yyyy-mm-dd', mindate=min_date, maxdate=max_date)
end_date_entry.pack(pady=5)

def save_diagram():
    file_path = tk.filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if file_path:
        fig.savefig(file_path, bbox_inches='tight')
        messagebox.showinfo("Save Diagram", f"Diagram saved successfully at:\n{file_path}")

# Button to update and display the selected diagram
# Button to update and display the selected diagram
def update_diagram():
    # Clear the figure and axes
    fig.clear()
    ax = fig.add_subplot(111)
    ax.set_facecolor('#f0f0f0')  # Set background color
    ax.grid(True, linestyle='--', alpha=0.6)  # Add grid lines
    selected_values = diagram_listbox.curselection()

    if not selected_values:
        return  # No valid selection, do nothing

    # Clear the axes before plotting new data
    ax.clear()

    # Clear the selected_dataframes list
    selected_dataframes = []

    # Use the actual dataframe names from diagram_options
    for index in selected_values:
        selected_dataframes.append(dataframes_dict[diagram_options[index]])

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

    # Create a dictionary to store the secondary axes for each DataFrame
    secondary_axes = {}

    # Define colors for each DataFrame
    colors = ['blue', 'green', 'red', 'purple', 'orange', 'brown']

    for index, (selected_dataframe, color) in enumerate(zip(selected_dataframes, colors)):
        selected_dataframe_filtered = selected_dataframe[
            (selected_dataframe['Data'] >= start_date) & (selected_dataframe['Data'] <= end_date)
        ]

        # Extract unit information from the last column values
        unit = selected_dataframe.iloc[-1, -1]  # Assuming the unit is in the last row of the last column
        lab = selected_dataframe.iloc[-2, -2]  # Assuming the unit is in the last row of the last column
        label = f"{lab} ({unit})"

        # Use twinx() to create a secondary y-axis for each additional DataFrame
        if index == 0:
            ax.plot(selected_dataframe_filtered['Data'], selected_dataframe_filtered['Wartość'],
                    label=label, color=color)
        else:
            secondary_axes[index] = ax.twinx()
            secondary_axes[index].plot(selected_dataframe_filtered['Data'], selected_dataframe_filtered['Wartość'],
                                       label=label, linestyle='dashed', color=color)

    # Set labels and legend for the primary y-axis
    ax.set_ylabel('Primary Y-Axis')
    ax.tick_params(axis='x', rotation=45)
    ax.yaxis.set_major_locator(plt.MaxNLocator(nbins='auto'))
    max_value_primary_axis = combined_dataframe['Wartość'].max()  # Get the maximum value within the displayed range
    max_value_primary_axis = float(max_value_primary_axis)
    #ax.set_yticks(np.linspace(0, max_value_primary_axis, num=7))
    ax.legend(loc='upper left')

    # Set labels and legends for the secondary y-axes
    for index, secondary_ax in secondary_axes.items():
        unit = selected_dataframes[index].iloc[-1, -1]  # Assuming the unit is in the last row of the last column
        secondary_ax.set_ylabel(f"Secondary Y-Axis {index} ({unit})")
        secondary_ax.yaxis.set_major_locator(plt.MaxNLocator(nbins='auto'))
        secondary_ax.legend(loc='upper right')

    canvas.draw()









update_button = tk.Button(app, text="Update Diagram", command=update_diagram)
update_button.pack(pady=10)



save_button = tk.Button(app, text="Save Diagram", command=save_diagram)
save_button.pack(pady=10)

# Matplotlib figure for displaying the diagram
fig = Figure(figsize=(8, 6), dpi=100)
ax = fig.add_subplot(111)
ax.set_facecolor('#f0f0f0')  # Set background color
ax.grid(True, linestyle='--', alpha=0.6)  # Add grid lines

canvas = FigureCanvasTkAgg(fig, master=app)
canvas.get_tk_widget().pack()

# Run the application
app.mainloop()
