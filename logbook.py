# Author: Florian Goldbach, Datum: 1.11.2023, Description: Logbook to save, edit, delete and view entries, utilizing Tkinter

import tkinter as tk
from tkinter import simpledialog, messagebox, font
import sqlite3
from datetime import datetime

# Setting up SQLite database
def setup_database():
    # Creating a connection to existing database, if database does not exist creating new database
    conn = sqlite3.connect("logbook.db")
    # Creating cursor object, used to execute SQL commands
    cur = conn.cursor()
    # Creating table, if it does not exist already (with SQL query)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY,
            title TEXT,
            content TEXT,
            entry_date TEXT
        )
    """
    )
    # Commiting changes (every change to database must be commited)
    conn.commit()
    # Closing connection
    conn.close()


# We are creating our own dialog window, as we have custom requirements
class EntryDialog(simpledialog.Dialog):
    # Constructor with parent (parent dialog), title and initalvalue paramenters
    def __init__(self, parent, title, initialvalue=None):
        self.initialvalue = initialvalue
        # calling constructor of superclass
        super().__init__(parent, title)

    # Creating and arranging widgets (labels, entry fields, text boxes etc.) inside the dialog box
    # Master is the parent widget, where they will be placed
    def body(self, master):
        # Packing title label and entry widget into master
        tk.Label(master, text="Title:", font=monospace_font).pack()
        self.title_entry = tk.Entry(master, width=30)
        self.title_entry.pack()

        # Packing content label and content text widget into master
        tk.Label(master, text="Content:", font=monospace_font).pack()
        self.content_text = tk.Text(master, width=50, height=20)
        self.content_text.pack()

        # Prepopulating entry widgets, when editing a logbook entry
        if self.initialvalue:
            self.title_entry.insert(tk.END, self.initialvalue["title"])
            self.content_text.insert(tk.END, self.initialvalue["content"])

        # The return statement defines the initial focus of the cursor (here the conten_text text widget)
        return self.title_entry

    # This method is called when the user clicks the OK-Button
    def apply(self):
        # Fetching current date and time and formatting to String
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Retrieving user input, and storing it in dictionary "self.result" for later use
        self.result = {
            "title": self.title_entry.get(),
            # Removing leading or trailing whitespaces
            "content": self.content_text.get("1.0", tk.END).strip(),
            "entry_date": current_time,
        }


# Loading entries from SQLite database
def load_entries():
    # Starting connection
    conn = sqlite3.connect("logbook.db")
    # Creating cursor object to execute SQL commands
    cur = conn.cursor()
    # SQL query to select relevant data from database
    cur.execute(
        "SELECT id, title, content, entry_date FROM entries ORDER BY entry_date ASC"
    )
    # Fetching all selected data and storing it in the entries variable
    entries = cur.fetchall()
    # Closing connection
    conn.close()
    # Returning the entries variable
    # - This is a list of tuples, where each tuple represents a row from the entries table in the database
    return entries


# Save entries to SQLite database
def save_entry(entry):
    conn = sqlite3.connect("logbook.db")
    cur = conn.cursor()
    # SQL query to insert a new row into the entries table in the database
    cur.execute(
        "INSERT INTO entries (title, content, entry_date) VALUES (?, ?, ?)",
        (entry["title"], entry["content"], entry["entry_date"]),
    )
    conn.commit()
    conn.close()


# Update entry in SQLite database
def update_entry(entry_id, entry):
    conn = sqlite3.connect("logbook.db")
    cur = conn.cursor()
    # SQL query to update the row in the entries, where the entry_id matches
    cur.execute(
        "UPDATE entries SET title = ?, content = ? WHERE id = ?",
        (entry["title"], entry["content"], entry_id),
    )
    conn.commit()
    conn.close()


# Delete the selected entry from SQLite database
def delete_entry_from_db(entry_id):
    conn = sqlite3.connect("logbook.db")
    cur = conn.cursor()
    # SQL query to delete the row from the entries table, where the entry_id matches
    cur.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()


# Deleting an entry from the logbook
def delete_entry():
    try:
        # Getting index of selected item
        # curselection() returns tuple of indices, that is why we use [0], even though there will only be 1 index in tuple
        index = listbox.curselection()[0]
        # Retrieving the entry_id from selected entry
        entry_id = entries[index][0]
        delete_entry_from_db(entry_id)
        refresh_listbox()
    # Hitting the delete "Delete Entry"-button without selecting entry
    except IndexError:
        messagebox.showerror("Selection Error", "Please select an item to delete.")


# Adding entry dialog
def add_entry():
    dialog = EntryDialog(root, "Add Log Entry")
    # First we check whether the user has exited the dialog successfully and then whether he input any data
    if dialog.result and (
        dialog.result.get("title").strip() or dialog.result.get("content").strip()
    ):
        save_entry(dialog.result)
        refresh_listbox()


def edit_entry():
    try:
        # Getting selected entry index (for listbox) and then entry_id (for database)
        index = listbox.curselection()[0]
        entry_id = entries[index][0]
        initial_value = {"title": entries[index][1], "content": entries[index][2]}
        # Passing initial (existing) entry content to EntryDialog
        dialog = EntryDialog(root, "Edit Log Entry", initialvalue=initial_value)
        # When the dialog is sucessfully closed, we update the database and refresh the listbox
        if dialog.result:
            update_entry(entry_id, dialog.result)
            refresh_listbox()
    # "Edit Entry"-button is clicked without selecting an entry
    except IndexError:
        messagebox.showerror("Selection Error", "Please select an entry to edit.")


# Viewing an entry in the log book
def view_entry():
    try:
        index = listbox.curselection()[0]
        entry = entries[index]
        messagebox.showinfo(
            entry[1], entry[2]
        )  # Title is at index 1, Content is at index 2
    # Pressing "View Entry"-Button without selecting entry
    except IndexError:
        messagebox.showerror("Selection Error", "Please select an entry to view.")


# Refreshing the contents of the listbox
def refresh_listbox():
    # Modifying the global variable "entries"
    global entries
    entries = load_entries()
    # Clearing all the current content of the listbox
    listbox.delete(0, tk.END)

    # We achieved the correct format by working with a monospaced font.
    # In this way we could format the Strings consistently..
    # ..to display the date/time information at the same position for each entry.
    max_title_length = 28

    # Looping through all entries
    for entry in entries:
        title = entry[1]
        date = entry[3]
        # In case the title is too long, we truncate it
        if len(title) > max_title_length:
            title = title[: max_title_length - 3] + "..."
        # We add blank spaces, to consistently reach same title length
        title = f"{title:<{max_title_length}}"
        # Displaying entry title and date/time
        entry_text = f"{title}  {date}"
        listbox.insert(tk.END, entry_text)


# Centering the dialog
def center_window(win):
    # Finishing all tasks, before size can be determined
    win.update_idletasks()
    # Determening window dimensions
    width = win.winfo_width()
    height = win.winfo_height()
    # Calculating center of screen
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    # Setting window geometry with a formatted string
    win.geometry("{}x{}+{}+{}".format(width, height, x, y))


# Setting up SQLite database
setup_database()

# Seting up the GUI
root = tk.Tk()
root.title("Logbook")

# Defining monospaced font (important for listbox entry layout)
monospace_font = font.Font(family="Courier", size=10, weight="bold")

# Setting a minimum size for the window
root.minsize(420, 400)

# Centering the window
center_window(root)

# Initializing the entries list
# (global variable, which is manipulated by refresh_listbox())
entries = load_entries()

# Listbox to display the log entries
# pack() method handles size and position of widgets in window
listbox = tk.Listbox(root, font=monospace_font)
listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Frame for the buttons
button_frame = tk.Frame(root)
button_frame.pack(padx=10, pady=10, fill=tk.X)

# Buttons to add, edit, delete, and view log entries
view_button = tk.Button(
    button_frame, text="View Entry", command=view_entry, font=monospace_font
)
add_button = tk.Button(
    button_frame, text="Add Entry", command=add_entry, font=monospace_font
)
edit_button = tk.Button(
    button_frame, text="Edit Entry", command=edit_entry, font=monospace_font
)
delete_button = tk.Button(
    button_frame, text="Delete Entry", command=delete_entry, font=monospace_font
)

view_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
add_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
edit_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
delete_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Refreshing the listbox with the current entries
refresh_listbox()

# Starting the GUI event loop
root.mainloop()
