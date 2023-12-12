import tkinter as tk
from tkinter import messagebox
from tkinter import Entry, Spinbox, ttk
from tkinter import Label

from tkcalendar import DateEntry
import psycopg2
from psycopg2 import sql
connection = psycopg2.connect(
    user=input("input username to database (default is postgres):"),
    password=input("Input password to database:"),
    host="localhost",
    port="5432",
    database="makarov"
)
connection.autocommit = True

current_sort_col_phones = 'id'
reversed_sort_phones = False
current_sort_col_socs = 'id'
reversed_sort_socs = False


class SoCOptions:
    def __init__(self, table_id, model):
        self.table_id = table_id
        self.model = model

    def str(self):
        return self.model

    def get_id(self):
        return self.table_id


SoC_combobox_widget = 0
soc_options = [SoCOptions]


def get_table_data(table_name):
    try:
        cursor = connection.cursor()
        if table_name == 'Phones':
            query = sql.SQL(f"""SELECT Phones.id AS id, Phones.Model AS model, Phones.Date_out AS date_out, SoCs.Model AS used_soc, Phones.Camera_count AS camera_count, Phones.Mass AS mass
                                FROM pg.Phones Phones
                                JOIN pg.SoCs ON Phones.Used_SoC = pg.SoCs.id
                                ORDER BY {current_sort_col_phones} {"DESC" if reversed_sort_phones else "ASC"};""")
        else:
            query = sql.SQL(f"""SELECT SoCs.id AS id, SoCs.Model AS model, SoCs.Date_out AS date_out, SoCs.tdp AS TDP, SoCs.core_count AS Core_count
             FROM pg.{table_name} SoCs
            ORDER BY {current_sort_col_socs} {"DESC" if reversed_sort_socs else "ASC"};""")
        cursor.execute(query)

        data = cursor.fetchall()

        column_names = [desc[0] for desc in cursor.description]

        cursor.close()

        return column_names, data

    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL:", error)
        return [], []


def add_record(tree, table_name, entry_widgets):
    try:
        cursor = connection.cursor()

        max_id = 0
        column_names, data = get_table_data(table_name)
        for i in data:
            if i[0] > max_id:
                max_id = i[0]
        col_str = ", ".join(column_names)
        pls_hld = ", ".join(['%s' for i in range(len(entry_widgets))])
        insert_query = sql.SQL(f"INSERT INTO pg.{table_name} ({col_str}) VALUES ({max_id + 1}, {pls_hld})")

        values = []
        for wid in entry_widgets:
            if isinstance(wid, ttk.Combobox):
                soc_names = [i.str() for i in soc_options]
                opt = soc_options[soc_names.index(wid.get())]
                values.append(opt.get_id())
            else:
                values.append(wid.get())

        cursor.execute(insert_query, values)

        cursor.close()

        update_tree(tree, table_name)
        messagebox.showinfo("Info", "Record added successfully.")
    except (Exception, psycopg2.Error) as error:
        messagebox.showerror("Error", f"Error adding record to database, {error}")


def edit_record(tree, table_name, entry_widgets):
    selected_item = tree.selection()

    if not selected_item:
        messagebox.showwarning("Warning", "Please select a record to edit.")
        return

    try:
        cursor = connection.cursor()
        record_id = tree.item(selected_item, "values")[0]
        column_names, _ = get_table_data(table_name)
        values = []
        for wid in entry_widgets:
            if isinstance(wid, ttk.Combobox):
                opt = soc_options[wid['values'].index(wid.get())]
                values.append(opt.get_id())
            else:
                values.append(wid.get())
        params = ""
        for i in range(len(values)):
            params += column_names[i + 1] + '= %s' + (', ' if i != len(values) - 1 else '')
        query = sql.SQL(f"UPDATE pg.{table_name} SET {params} WHERE id = %s")
        cursor.execute(query, (*values, record_id))

        cursor.close()
        update_tree(tree, table_name)
        messagebox.showinfo("Info", "Record updated successfully.")

    except (Exception, psycopg2.Error) as error:
        messagebox.showerror("Error", f"Error editing record, {error}")


def delete_record(tree, table_name):
    selected_item = tree.selection()

    if not selected_item:
        messagebox.showwarning("Warning", "Please select a record to delete.")
        return

    confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete this record?")

    if not confirmation:
        return

    try:
        cursor = connection.cursor()
        record_id = tree.item(selected_item, "values")[0]
        query = sql.SQL(f"DELETE FROM pg.{table_name} WHERE id = %s")
        cursor.execute(query, (record_id,))
        cursor.close()
        tree.delete(selected_item)
        messagebox.showinfo("Info", "Record deleted successfully.")

    except (Exception, psycopg2.Error) as error:
        messagebox.showerror("Error", f"Error deleting record from database, {error}")

from datetime import datetime

def convert_date_format(value):
    formatted_date = value.strftime("%d.%m.%Y")
    return formatted_date


def update_tree(tree, table_name):
    for i in tree.get_children():
        tree.delete(i)
    column_names, data = get_table_data(table_name)
    tree["columns"] = tuple(column_names)

    def change_sort_params(col):
        if (table_name == 'Phones'):
            global current_sort_col_phones
            current_sort_col_phones = col
            global reversed_sort_phones
            reversed_sort_phones = not reversed_sort_phones
        else:
            global current_sort_col_socs
            current_sort_col_socs = col
            global reversed_sort_socs
            reversed_sort_socs = not reversed_sort_socs
        update_tree(tree, table_name)
    date_out_column_index = column_names.index('date_out')
    for column_name in column_names:
        tree.heading(column_name, text=column_name, command=lambda _col=column_name: change_sort_params(_col))
    for row in data:
        lst = list(row)
        lst[date_out_column_index] = convert_date_format(lst[date_out_column_index])
        tree.insert("", tk.END, values=tuple(lst))  # Exclude the 'id' column

    displaycolumns = []
    for col in tree["columns"]:
        if not "%s" % col == "id":
            displaycolumns.append(col)
    tree["displaycolumns"] = displaycolumns
    return column_names, data


def get_values_for_combobox_soc():
    soc_options_raw = get_table_data("SoCs")[1]  # Get SoCs for dropdown
    global soc_options
    soc_options = [SoCOptions(i[0], i[1]) for i in soc_options_raw]
    return [i.str() for i in soc_options]


def on_treeview_click(event, tree, entry_widgets):
    try:
        item = tree.selection()[0]
        values = tree.item(item, 'values')
        for i in range(len(entry_widgets)):
            if isinstance(entry_widgets[i], ttk.Combobox):
                entry_widgets[i].set(values[i+1])
            else:
                entry_widgets[i].delete(0, tk.END)  # Clear the current value
                entry_widgets[i].insert(0, values[i+1])
    except Exception:
        pass

def display_table_data(table_name):
    frame = ttk.Frame(tab_notebook)

    tree = ttk.Treeview(frame, show="headings")
    column_names, _ = update_tree(tree, table_name)
    entry_widgets = []
    tree.pack(expand=True, fill=tk.BOTH)
    tree.bind('<ButtonRelease-1>', lambda event: on_treeview_click(event, tree, entry_widgets))

    add_button = ttk.Button(frame, text="Add", command=lambda: add_record(tree, table_name, entry_widgets))
    edit_button = ttk.Button(frame, text="Edit", command=lambda: edit_record(tree, table_name, entry_widgets))
    delete_button = ttk.Button(frame, text="Delete", command=lambda: delete_record(tree, table_name))
    add_button.pack(side=tk.RIGHT, padx=5)
    edit_button.pack(side=tk.RIGHT, padx=5)
    delete_button.pack(side=tk.RIGHT, padx=5)

    entry_widgets_names = []
    for col_name in column_names[1:]:  # Exclude the 'id' column
        if col_name == "model":
            entry_widget = Entry(frame)
        elif col_name == "date_out":
            entry_widget = DateEntry(frame, width=12, background="darkblue", foreground="white", borderwidth=2,
                                     locale="ru_RU")
        elif col_name == "tdp":
            entry_widget = Entry(frame, validate="key")
        elif col_name == "mass":
            entry_widget = Entry(frame, validate="key")
        elif col_name == "used_soc":
            global SoC_combobox_widget
            SoC_combobox_widget = ttk.Combobox(frame, values=[], state="readonly",
                                               postcommand=lambda: SoC_combobox_widget.configure(
                                                   values=get_values_for_combobox_soc()))
            SoC_combobox_widget.configure(values=get_values_for_combobox_soc())
            entry_widget = SoC_combobox_widget
        elif col_name in ("camera_count", "core_count"):
            entry_widget = Spinbox(frame, name=col_name, from_=0, to=10000)
        else:
            entry_widget = Entry(frame)
        entry_widgets_names.append(Label(frame, text=col_name))
        entry_widgets.append(entry_widget)
        entry_widgets_names[-1].pack(side=tk.LEFT, padx=5)
        entry_widget.pack(side=tk.LEFT, padx=5)

    tab_notebook.add(frame, text=table_name)


window = tk.Tk()
window.title("Table Viewer")

name = ttk.Label(window, text="""Макаров Дмитрий Вадимович, 4 курс, 4 группа, 2023\n
Чтобы изменить запись, нажмите на интересующую строку, внизу измените что-нибудь, и нажмите Edit.\n
Чтобы отсортировать, нажмите на заголовки столбцов""")

tab_notebook = ttk.Notebook(window)

display_table_data("SoCs")
display_table_data("Phones")
get_values_for_combobox_soc()
name.pack(expand=True, fill=tk.BOTH)
tab_notebook.pack(expand=True, fill=tk.BOTH)

window.mainloop()
connection.close()
