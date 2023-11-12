import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import Entry, Spinbox, ttk
from tkinter import Label

from tkcalendar import DateEntry
import psycopg2
from psycopg2 import sql

connection = psycopg2.connect(
    user="postgres",
    # password=input("Input password to database:")
    password="mmrbndber404mnf",
    host="localhost",
    port="5432",
    database="postgres"
)
connection.autocommit = True


# Function to connect to PostgreSQL and fetch data for a specific table
def get_table_data(table_name):
    try:
        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Execute a SELECT query to fetch data from the specified table
        query = sql.SQL(f"SELECT * FROM pg.{table_name}")
        cursor.execute(query)

        # Fetch all rows from the result set
        data = cursor.fetchall()

        # Get the column names excluding 'id'
        column_names = [desc[0] for desc in cursor.description]

        # Close the cursor and connection
        cursor.close()

        return column_names, data

    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL:", error)
        return [], []


def add_record(tree, table_name, entry_widgets):
    try:
        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Prepare the INSERT query based on the table name and column names
        max_id = 0
        column_names, data = get_table_data(table_name)
        for i in data:
            if i[0] > max_id:
                max_id = i[0]
        col_str = ", ".join(column_names)
        pls_hld = ", ".join(['%s' for i in range(len(entry_widgets))])
        insert_query = sql.SQL(f"INSERT INTO pg.{table_name} ({col_str}) VALUES ({max_id + 1}, {pls_hld})")

        # Get the values from the entry widgets
        values = [widget.get() for widget in entry_widgets]

        # Execute the INSERT query with the values
        cursor.execute(insert_query, values)

        # Close the cursor and connection
        cursor.close()

        update_tree(tree, table_name)
        messagebox.showinfo("Info", "Record added successfully.")
    except (Exception, psycopg2.Error) as error:
        messagebox.showerror("Error", f"Error adding record to database, {error}")

# Function to handle the "Edit" button click
def edit_record():
    messagebox.showinfo("Info", "Edit operation not implemented yet.")


# Function to handle the "Delete" button click
def delete_record(tree, table_name):
    # Get the selected item in the treeview
    selected_item = tree.selection()

    if not selected_item:
        messagebox.showwarning("Warning", "Please select a record to delete.")
        return

    # Ask for confirmation before deleting the record
    confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete this record?")

    if not confirmation:
        return

    try:
        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Get the id of the selected record
        record_id = tree.item(selected_item, "values")[0]

        # Execute a DELETE query to delete the record
        query = sql.SQL(f"DELETE FROM pg.{table_name} WHERE id = %s")
        cursor.execute(query, (record_id,))

        # Close the cursor and connection
        cursor.close()

        # Delete the selected item from the treeview
        tree.delete(selected_item)

        messagebox.showinfo("Info", "Record deleted successfully.")

    except (Exception, psycopg2.Error) as error:
        messagebox.showerror("Error", f"Error deleting record from database, {error}")


def update_tree(tree, table_name):
    for i in tree.get_children():
        tree.delete(i)
    column_names, data = get_table_data(table_name)
    tree["columns"] = tuple(column_names)
    # Define column headings
    for column_name in column_names:
        tree.heading(column_name, text=column_name)

    # Populate the treeview with data
    for row in data:
        tree.insert("", tk.END, values=row)  # Exclude the 'id' column

    displaycolumns = []
    for col in tree["columns"]:
        if not "%s" % col == "id":
            displaycolumns.append(col)
    tree["displaycolumns"] = displaycolumns
    return column_names, data

# Function to display data for the selected table
def display_table_data(table_name):

    # Create a new frame for the tab
    frame = ttk.Frame(tab_notebook)

    # Create a treeview widget to display data in a tabular format
    tree = ttk.Treeview(frame, show="headings")
    column_names, _ = update_tree(tree, table_name)

    # Pack the treeview to the frame
    tree.pack(expand=True, fill=tk.BOTH)
    entry_widgets = []
    # Create buttons for add, edit, and delete operations
    add_button = ttk.Button(frame, text="Add", command=lambda: add_record(tree, table_name, entry_widgets))
    edit_button = ttk.Button(frame, text="Edit", command=edit_record)
    delete_button = ttk.Button(frame, text="Delete", command=lambda: delete_record(tree, table_name))

    # Pack the buttons to the right side of the frame
    add_button.pack(side=tk.RIGHT, padx=5)
    edit_button.pack(side=tk.RIGHT, padx=5)
    delete_button.pack(side=tk.RIGHT, padx=5)

    # Create a row of widgets for adding records

    entry_widgets_names = []
    for col_name in column_names[1:]:  # Exclude the 'id' column
        if col_name == "model":
            entry_widget = Entry(frame)
        elif col_name == "date_out":
            entry_widget = DateEntry(frame, width=12, background="darkblue", foreground="white", borderwidth=2)
        elif col_name == "tdp":
            entry_widget = Entry(frame, validate="key")
        elif col_name == "mass":
            entry_widget = Entry(frame, validate="key")
        elif col_name == "used_soc":
            soc_options = get_table_data("SoCs")[1]  # Get SoCs for dropdown
            soc_options = [i[1] for i in soc_options]
            entry_widget = ttk.Combobox(frame, values=soc_options, state="readonly")
        elif col_name in ("camera_count", "core_count"):
            entry_widget = Spinbox(frame, name=col_name, from_=0, to=10000)
        else:
            entry_widget = Entry(frame)
        entry_widgets_names.append(Label(frame, text=col_name))
        entry_widgets.append(entry_widget)
        entry_widgets_names[-1].pack(side=tk.LEFT,padx=5)
        entry_widget.pack(side=tk.LEFT, padx=5)

    # Add the frame to the notebook
    tab_notebook.add(frame, text=table_name)


# Create the main tkinter window
window = tk.Tk()
window.title("Table Viewer")

# Create a notebook (tabbed interface)
tab_notebook = ttk.Notebook(window)

# Display data for the "pg.SoCs" table
display_table_data("SoCs")

# Display data for the "pg.Phones" table
display_table_data("Phones")

# Pack the notebook to the window
tab_notebook.pack(expand=True, fill=tk.BOTH)

# Run the tkinter event loop
window.mainloop()

connection.close()
