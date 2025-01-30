import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

# Database Connection Details
DATABASE = "BloodBankManagement_Normalized"
USER = "postgres"
PASSWORD = "db@12db"
HOST = "localhost"

def connect_db():
    """Connect to the PostgreSQL database server."""
    try:
        return psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
    except psycopg2.DatabaseError as error:
        messagebox.showerror("Database Connection Error", str(error))
        return None

def load_data(tree, query, *args):
    """Generic function to load data into the Treeview."""
    tree.delete(*tree.get_children())
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute(query, args)
            for row in cursor:
                tree.insert('', 'end', values=row)
        finally:
            cursor.close()
            db.close()

def insert_update_data(query, args, tree, refresh_query, message):
    """Generic function to handle both insert and update operations."""
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute(query, args)
            db.commit()
            messagebox.showinfo('Success', message)
            load_data(tree, refresh_query)  # Refresh the data displayed
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', f'Failed operation: {e}')
        finally:
            cursor.close()
            db.close()

def delete_data(query, identifier, tree, refresh_query, message):
    """Generic function to delete data from the database."""
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute(query, (identifier,))
            db.commit()
            messagebox.showinfo('Success', message)
            load_data(tree, refresh_query)  # Refresh the data displayed
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', f'Failed to delete: {e}')
        finally:
            cursor.close()
            db.close()

def create_tab(tab_control, title, columns, insert_query, update_query, delete_query, load_query):
    """Function to create each tab dynamically."""
    tab = ttk.Frame(tab_control)
    tree = ttk.Treeview(tab, columns=columns, show='headings')
    tree.grid(row=0, column=0, columnspan=3, sticky='nsew')
    for col in columns:
        tree.heading(col, text=col)

    # Entry fields setup
    entries = {}
    for idx, column in enumerate(columns):
        label = ttk.Label(tab, text=column)
        label.grid(row=1, column=idx)
        entry = ttk.Entry(tab)
        entry.grid(row=2, column=idx)
        entries[column] = entry

    def insert_record():
        args = tuple(entries[col].get() for col in columns)
        insert_update_data(insert_query, args, tree, load_query, "Record added successfully.")

    def update_record():
        args = tuple(entries[col].get() for col in columns) + (tree.item(tree.selection(), 'values')[0],)
        insert_update_data(update_query, args, tree, load_query, "Record updated successfully.")

    def delete_record():
        identifier = tree.item(tree.selection(), 'values')[0]
        delete_data(delete_query, identifier, tree, load_query, "Record deleted successfully.")

    ttk.Button(tab, text="Add", command=insert_record).grid(row=3, column=0)
    ttk.Button(tab, text="Update", command=update_record).grid(row=3, column=1)
    ttk.Button(tab, text="Delete", command=delete_record).grid(row=3, column=2)

    load_data(tree, load_query)  # Initial load of data
    return tab

def main():
    root = tk.Tk()
    root.title("Blood Bank Management System")
    root.geometry("800x600")

    tab_control = ttk.Notebook(root)

    # Define SQL queries for operations
    donor_columns = ('bd_id', 'bd_name', 'bd_age', 'bd_Bgroup', 'bd_sex')
    donor_insert_query = "INSERT INTO Blood_Donor VALUES (%s, %s, %s, %s, %s)"
    donor_update_query = "UPDATE Blood_Donor SET bd_name=%s, bd_age=%s, bd_Bgroup=%s, bd_sex=%s WHERE bd_id=%s"
    donor_delete_query = "DELETE FROM Blood_Donor WHERE bd_id=%s"
    donor_load_query = "SELECT * FROM Blood_Donor"

    # Create tabs
    blood_donor_tab = create_tab(tab_control, "Blood Donor", donor_columns, donor_insert_query, donor_update_query, donor_delete_query, donor_load_query)
    tab_control.add(blood_donor_tab, text="Blood Donor")

    tab_control.pack(expand=1, fill="both")
    root.mainloop()

if __name__ == "__main__":
    main()
