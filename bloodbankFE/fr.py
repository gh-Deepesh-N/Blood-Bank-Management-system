import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
DATABASE = "BloodBankManagement_Normalized"
USER = "postgres"
PASSWORD = "db@12db"
HOST = "localhost"
def connect_db():
    """ Connect to the PostgreSQL database server """
    try:
        conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        messagebox.showerror("Database Connection Error", str(error))
        return None
def insert_blood_donor(name, age, blood_group, gender, tree):
    """ Insert a blood donor into the database """
    db = connect_db()
    if db is not None:
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO Blood_Donor (bd_name, bd_age, bd_Bgroup, bd_sex) VALUES (%s, %s, %s, %s)",
                           (name, age, blood_group, gender))
            db.commit()
            messagebox.showinfo('Success', 'Blood donor added successfully.')
            load_donors(tree)  # Refresh the list after insertion
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', 'Failed to add blood donor.')
        finally:
            cursor.close()
            db.close()

def delete_blood_donor(bd_id, tree):
    """ Delete a blood donor from the database """
    db = connect_db()
    if db is not None:
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM Blood_Donor WHERE bd_id = %s", (bd_id,))
            db.commit()
            messagebox.showinfo('Success', 'Blood donor deleted successfully.')
            load_donors(tree)  # Refresh the list after deletion
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', 'Failed to delete blood donor.')
        finally:
            cursor.close()
            db.close()

def load_donors(tree):
    """ Load the donor data into the Treeview """
    for i in tree.get_children():
        tree.delete(i)
    db = connect_db()
    if db is not None:
        cursor = db.cursor()
        try:
            cursor.execute("SELECT bd_id, bd_name, bd_age, bd_Bgroup, bd_sex FROM Blood_Donor")
            for row in cursor:
                tree.insert('', 'end', values=row)
        finally:
            cursor.close()
            db.close()

def load_blood_specimens(tree):
    """ Load the blood specimen data into the Treeview """
    for i in tree.get_children():
        tree.delete(i)
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("SELECT specimen_number, b_group, status, bd_id, expiration_date FROM BloodSpecimen")
            for row in cursor:
                tree.insert('', 'end', values=row)
        finally:
            cursor.close()
            db.close()

def insert_blood_specimen(specimen_number, b_group, status, bd_id, expiration_date, tree):
    """ Insert a blood specimen into the database """
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO BloodSpecimen (specimen_number, b_group, status, bd_id, expiration_date) 
                VALUES (%s, %s, %s, %s, %s)
            """, (specimen_number, b_group, status, bd_id, expiration_date))
            db.commit()
            messagebox.showinfo('Success', 'Blood specimen added successfully.')
            load_blood_specimens(tree)  # Refresh the list after insertion
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', 'Failed to add blood specimen: ' + str(e))
            print("Error: ", e)  # Print the error to the console or log it
        finally:
            cursor.close()
            db.close()

def delete_blood_specimen(specimen_number, tree):
    """ Delete a blood specimen from the database """
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM BloodSpecimen WHERE specimen_number = %s", (specimen_number,))
            db.commit()
            if cursor.rowcount == 0:
                messagebox.showwarning('Warning', 'No record found to delete.')
            else:
                messagebox.showinfo('Success', 'Blood specimen deleted successfully.')
            load_blood_specimens(tree)  # Refresh the list after deletion
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', 'Failed to delete blood specimen: ' + str(e))
            print("Error: ", e)  # Print the error to the console or log it
        finally:
            cursor.close()
            db.close()


def update_blood_specimen(specimen_number, b_group, status, bd_id, expiration_date, tree):
    """ Update a blood specimen in the database """
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            sql = """UPDATE BloodSpecimen SET b_group=%s, status=%s, bd_id=%s, expiration_date=%s 
                     WHERE specimen_number=%s"""
            cursor.execute(sql, (b_group, status, bd_id, expiration_date, specimen_number))
            db.commit()
            messagebox.showinfo('Success', 'Blood specimen updated successfully.')
            load_blood_specimens(tree)  # Refresh the list after update
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', 'Failed to update blood specimen: ' + str(e))
        finally:
            cursor.close()
            db.close()


def create_blood_specimen_tab(tab_control):
    tab = ttk.Frame(tab_control)
    tab.columnconfigure(1, weight=1)  # Make the entry fields expand more

    # Setting up the Treeview
    tree = ttk.Treeview(tab, columns=('Specimen Number', 'Blood Group', 'Status', 'Donor ID', 'Expiration Date'), show='headings')
    tree.grid(row=0, column=0, columnspan=4, sticky='nsew')
    for col in tree['columns']:
        tree.heading(col, text=col.replace('_', ' ').title())

    # Entry fields for input
    labels = ['Specimen Number', 'Blood Group', 'Status', 'Donor ID', 'Expiration Date']
    entries = {}
    for i, label in enumerate(labels):
        ttk.Label(tab, text=label+":").grid(row=i+1, column=0, sticky=tk.W)
        entry = ttk.Entry(tab)
        entry.grid(row=i+1, column=1, sticky=tk.EW)
        entries[label] = entry

    # Buttons for operations
    ttk.Button(tab, text="Add Specimen", command=lambda: insert_blood_specimen(
        entries['Specimen Number'].get(), entries['Blood Group'].get(), entries['Status'].get(), 
        entries['Donor ID'].get(), entries['Expiration Date'].get(), tree)).grid(row=6, column=0, sticky=tk.W)

    ttk.Button(tab, text="Update Specimen", command=lambda: update_blood_specimen(
        entries['Specimen Number'].get(), entries['Blood Group'].get(), entries['Status'].get(), 
        entries['Donor ID'].get(), entries['Expiration Date'].get(), tree)).grid(row=6, column=1, sticky=tk.E)

    ttk.Button(tab, text="Delete Specimen", command=lambda: delete_blood_specimen(
        entries['Specimen Number'].get(), tree)).grid(row=7, column=0, sticky=tk.W)

    load_blood_specimens(tree)  # Load data initially
    return tab


def load_hospital_info(tree):
    """ Load the hospital data into the Treeview """
    for i in tree.get_children():
        tree.delete(i)
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("SELECT hosp_id, hosp_name, hosp_needed_bgrp, hosp_needed_bqnty, city_id FROM hospital_info")
            for row in cursor:
                tree.insert('', 'end', values=row)
        finally:
            cursor.close()
            db.close()
def load_diseasefinders(tree):
    """ Load the diseasefinder data along with their contacts into the Treeview """
    for i in tree.get_children():
        tree.delete(i)
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("""
                SELECT df.dfind_id, df.dfind_name, dc.dfind_phno
                FROM diseasefinder df
                LEFT JOIN diseasefinder_contact dc ON df.dfind_id = dc.dfind_id
            """)
            for row in cursor:
                tree.insert('', 'end', values=row)
        finally:
            cursor.close()
            db.close()
def load_diseasefinders(tree):
    for i in tree.get_children():
        tree.delete(i)
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("SELECT df.dfind_id, df.dfind_name, dc.dfind_phno FROM diseasefinder df LEFT JOIN diseasefinder_contact dc ON df.dfind_id = dc.dfind_id")
            for row in cursor:
                tree.insert('', 'end', values=row)
        finally:
            cursor.close()
            db.close()

# Insert new DiseaseFinder
def insert_diseasefinder(dfind_id, dfind_name, dfind_phno, tree):
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO diseasefinder (dfind_id, dfind_name) VALUES (%s, %s)", (dfind_id, dfind_name))
            cursor.execute("INSERT INTO diseasefinder_contact (dfind_id, dfind_phno) VALUES (%s, %s)", (dfind_id, dfind_phno))
            db.commit()
            messagebox.showinfo('Success', 'Disease Finder added successfully.')
            load_diseasefinders(tree)
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', 'Failed to add Disease Finder: ' + str(e))
        finally:
            cursor.close()
            db.close()

# Delete existing DiseaseFinder
def delete_diseasefinder(dfind_id, tree):
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM diseasefinder_contact WHERE dfind_id = %s", (dfind_id,))
            cursor.execute("DELETE FROM diseasefinder WHERE dfind_id = %s", (dfind_id,))
            db.commit()
            messagebox.showinfo('Success', 'Disease Finder deleted successfully.')
            load_diseasefinders(tree)
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', 'Failed to delete Disease Finder: ' + str(e))
        finally:
            cursor.close()
            db.close()

# Update existing DiseaseFinder
def update_diseasefinder(dfind_id, new_name, new_phno, tree):
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("UPDATE diseasefinder SET dfind_name = %s WHERE dfind_id = %s", (new_name, dfind_id))
            cursor.execute("UPDATE diseasefinder_contact SET dfind_phno = %s WHERE dfind_id = %s", (new_phno, dfind_id))
            db.commit()
            messagebox.showinfo('Success', 'Disease Finder updated successfully.')
            load_diseasefinders(tree)
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', 'Failed to update Disease Finder: ' + str(e))
        finally:
            cursor.close()
            db.close()

# GUI setup for DiseaseFinder Tab
def create_diseasefinder_tab(tab_control):
    tab = ttk.Frame(tab_control)

    # Grid configuration for better alignment (Converted to use pack for consistency)
    tree = ttk.Treeview(tab, columns=('Disease Finder ID', 'Name', 'Phone Number'), show='headings')
    tree.pack(fill='both', expand=True)

    # Scrollbars for the Treeview
    scrollbar_vertical = ttk.Scrollbar(tab, orient='vertical', command=tree.yview)
    scrollbar_vertical.pack(side='right', fill='y')
    scrollbar_horizontal = ttk.Scrollbar(tab, orient='horizontal', command=tree.xview)
    scrollbar_horizontal.pack(side='bottom', fill='x')

    tree.configure(yscrollcommand=scrollbar_vertical.set, xscrollcommand=scrollbar_horizontal.set)

    # Configure the tree headings
    for col in tree['columns']:
        tree.heading(col, text=col.replace('_', ' ').title())

    # Entry setup for Disease Finder Info
    input_frame = ttk.Frame(tab)
    input_frame.pack(fill='x')

    ttk.Label(input_frame, text="Disease Finder ID:").pack(side='left')
    dfind_id_entry = ttk.Entry(input_frame)
    dfind_id_entry.pack(side='left', fill='x', expand=True)

    ttk.Label(input_frame, text="Name:").pack(side='left')
    dfind_name_entry = ttk.Entry(input_frame)
    dfind_name_entry.pack(side='left', fill='x', expand=True)

    ttk.Label(input_frame, text="Phone Number:").pack(side='left')
    dfind_phno_entry = ttk.Entry(input_frame)
    dfind_phno_entry.pack(side='left', fill='x', expand=True)

    # Buttons for Disease Finder Info
    button_frame = ttk.Frame(tab)
    button_frame.pack(fill='x')

    ttk.Button(button_frame, text="Add Entry", command=lambda: insert_diseasefinder(dfind_id_entry.get(), dfind_name_entry.get(), dfind_phno_entry.get(), tree)).pack(side='left', fill='x', expand=True)
    ttk.Button(button_frame, text="Update Entry", command=lambda: update_diseasefinder(dfind_id_entry.get(), dfind_name_entry.get(), dfind_phno_entry.get(), tree)).pack(side='left', fill='x', expand=True)
    ttk.Button(button_frame, text="Delete Selected", command=lambda: delete_diseasefinder(tree.item(tree.selection(), 'values')[0], tree)).pack(side='left', fill='x', expand=True)

    load_diseasefinders(tree)
    return tab


def load_hospital_info(tree):
    """ Load the hospital data into the Treeview """
    for i in tree.get_children():
        tree.delete(i)
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("SELECT hosp_id, hosp_name, hosp_needed_bgrp, hosp_needed_bqnty, city_id FROM hospital_info")
            for row in cursor:
                tree.insert('', 'end', values=row)
        finally:
            cursor.close()
            db.close()

def insert_hospital_info(hosp_id, hosp_name, needed_bgrp, needed_bqnty, city_id, tree):
    """ Insert a new hospital into the database """
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("SELECT city_id FROM city WHERE city_id = %s", (city_id,))
            if cursor.fetchone() is None:
                messagebox.showerror('Error', 'No city found with ID: {}'.format(city_id))
                return
            cursor.execute("INSERT INTO hospital_info (hosp_id, hosp_name, hosp_needed_bgrp, hosp_needed_bqnty, city_id) VALUES (%s, %s, %s, %s, %s)", (hosp_id, hosp_name, needed_bgrp, needed_bqnty, city_id))
            db.commit()
            messagebox.showinfo('Success', 'Hospital information added successfully.')
            load_hospital_info(tree)
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', 'Failed to add hospital information: ' + str(e))
        finally:
            cursor.close()
            db.close()

def update_hospital_info(hosp_id, hosp_name, needed_bgrp, needed_bqnty, city_id, tree):
    """ Update hospital information in the database """
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("SELECT city_id FROM city WHERE city_id = %s", (city_id,))
            if cursor.fetchone() is None:
                messagebox.showerror('Error', 'No city found with ID: {}'.format(city_id))
                return
            cursor.execute("UPDATE hospital_info SET hosp_name=%s, hosp_needed_bgrp=%s, hosp_needed_bqnty=%s, city_id=%s WHERE hosp_id=%s", (hosp_name, needed_bgrp, needed_bqnty, city_id, hosp_id))
            db.commit()
            messagebox.showinfo('Success', 'Hospital information updated successfully.')
            load_hospital_info(tree)
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', 'Failed to update hospital information: ' + str(e))
        finally:
            cursor.close()
            db.close()

def delete_hospital_info(hosp_id, tree):
    """ Delete hospital information from the database """
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM hospital_info WHERE hosp_id = %s", (hosp_id,))
            db.commit()
            messagebox.showinfo('Success', 'Hospital information deleted successfully.')
            load_hospital_info(tree)
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', 'Failed to delete hospital information: ' + str(e))
        finally:
            cursor.close()
            db.close()

def create_hospital_info_tab(tab_control):
    tab = ttk.Frame(tab_control)
    tab.pack(fill='both', expand=True)

    # Creating a Treeview widget for hospital data
    tree = ttk.Treeview(tab, columns=('Hospital ID', 'Hospital Name', 'Needed Blood Group', 'Needed Quantity', 'City ID'), show='headings')
    tree.heading('Hospital ID', text='Hospital ID')
    tree.heading('Hospital Name', text='Hospital Name')
    tree.heading('Needed Blood Group', text='Needed Blood Group')
    tree.heading('Needed Quantity', text='Needed Quantity')
    tree.heading('City ID', text='City ID')
    tree.grid(row=1, column=0, columnspan=5, sticky='nsew')

    # Scrollbars for the Treeview
    scrollbar_vertical = ttk.Scrollbar(tab, orient='vertical', command=tree.yview)
    scrollbar_vertical.grid(row=1, column=5, sticky='ns')
    scrollbar_horizontal = ttk.Scrollbar(tab, orient='horizontal', command=tree.xview)
    scrollbar_horizontal.grid(row=2, column=0, columnspan=5, sticky='ew')
    tree.configure(yscrollcommand=scrollbar_vertical.set, xscrollcommand=scrollbar_horizontal.set)

    # Labels and Entry fields for hospital details
    ttk.Label(tab, text="Hospital ID:").grid(row=0, column=0)
    hosp_id_entry = ttk.Entry(tab)
    hosp_id_entry.grid(row=0, column=1)

    ttk.Label(tab, text="Hospital Name:").grid(row=0, column=2)
    hosp_name_entry = ttk.Entry(tab)
    hosp_name_entry.grid(row=0, column=3)

    ttk.Label(tab, text="Needed Blood Group:").grid(row=3, column=0)
    needed_bgrp_entry = ttk.Entry(tab)
    needed_bgrp_entry.grid(row=3, column=1)

    ttk.Label(tab, text="Needed Quantity:").grid(row=3, column=2)
    needed_bqnty_entry = ttk.Entry(tab)
    needed_bqnty_entry.grid(row=3, column=3)

    ttk.Label(tab, text="City ID:").grid(row=3, column=4)
    city_id_entry = ttk.Entry(tab)
    city_id_entry.grid(row=3, column=5)

    # Buttons for CRUD operations
    ttk.Button(tab, text="Add Hospital", command=lambda: insert_hospital_info(hosp_id_entry.get(), hosp_name_entry.get(), needed_bgrp_entry.get(), needed_bqnty_entry.get(), city_id_entry.get(), tree)).grid(row=4, column=0, columnspan=2)
    ttk.Button(tab, text="Update Hospital", command=lambda: update_hospital_info(hosp_id_entry.get(), hosp_name_entry.get(), needed_bgrp_entry.get(), needed_bqnty_entry.get(), city_id_entry.get(), tree)).grid(row=4, column=2, columnspan=2)
    ttk.Button(tab, text="Delete Hospital", command=lambda: delete_hospital_info(hosp_id_entry.get(), tree)).grid(row=4, column=4, columnspan=2)

    # Initial data loading
    load_hospital_info(tree)

    return tab


def load_recipients(tree):
    """ Load the recipient data along with their contacts into the Treeview """
    for i in tree.get_children():
        tree.delete(i)
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("""
                SELECT r.reci_id, r.reci_name, r.reci_age, r.reci_bgrp, r.reci_bqnty, r.reci_sex, r.reci_reg_date, c.reci_phno
                FROM recipient r
                LEFT JOIN recipient_contact c ON r.reci_id = c.reci_id
            """)
            for row in cursor:
                tree.insert('', 'end', values=row)
        finally:
            cursor.close()
            db.close()


def insert_recipient(reci_id, reci_name, reci_age, reci_bgrp, reci_bqty, reci_sex, reci_reg_date, reci_phno, tree):
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO recipient (reci_id, reci_name, reci_age, reci_bgrp, reci_bqnty, reci_sex, reci_reg_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (reci_id, reci_name, reci_age, reci_bgrp, reci_bqty, reci_sex, reci_reg_date))
            cursor.execute("""
                INSERT INTO recipient_contact (reci_id, reci_phno)
                VALUES (%s, %s)
            """, (reci_id, reci_phno))
            db.commit()
            messagebox.showinfo('Success', 'Recipient and Contact information added successfully.')
            load_recipients(tree)
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', f'Failed to add Recipient information.\n{e}')
        finally:
            cursor.close()
            db.close()
def update_recipient(reci_id, reci_name, reci_age, reci_bgrp, reci_bqty, reci_sex, reci_reg_date, reci_phno, tree):
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE recipient
                SET reci_name=%s, reci_age=%s, reci_bgrp=%s, reci_bqnty=%s, reci_sex=%s, reci_reg_date=%s
                WHERE reci_id=%s
            """, (reci_name, reci_age, reci_bgrp, reci_bqty, reci_sex, reci_reg_date, reci_id))
            cursor.execute("""
                UPDATE recipient_contact
                SET reci_phno=%s
                WHERE reci_id=%s
            """, (reci_phno, reci_id))
            db.commit()
            messagebox.showinfo('Success', 'Recipient information updated successfully.')
            load_recipients(tree)
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', 'Failed to update Recipient information.\n{e}')
        finally:
            cursor.close()
            db.close()



def delete_recipient(reci_id, tree):
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM recipient_contact WHERE reci_id = %s", (reci_id,))
            cursor.execute("DELETE FROM recipient WHERE reci_id = %s", (reci_id,))
            db.commit()
            messagebox.showinfo('Success', 'Recipient information deleted successfully.')
            load_recipients(tree)
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', 'Failed to delete Recipient information.\n{e}')
        finally:
            cursor.close()
            db.close()


def create_recipient_tab(tab_control):
    tab = ttk.Frame(tab_control)
    tab.pack(fill='both', expand=True)

    # Treeview setup
    tree = ttk.Treeview(tab, columns=('ID', 'Name', 'Age', 'Blood Group', 'Quantity', 'Sex', 'Registration Date', 'Phone Number'), show='headings')
    tree.pack(fill='both', expand=True)
    for col in tree['columns']:
        tree.heading(col, text=col.replace('_', ' ').title())

    # Add scrollbars
    scrollbar_vertical = ttk.Scrollbar(tab, orient='vertical', command=tree.yview)
    scrollbar_vertical.pack(side='right', fill='y')
    scrollbar_horizontal = ttk.Scrollbar(tab, orient='horizontal', command=tree.xview)
    scrollbar_horizontal.pack(side='bottom', fill='x')
    tree.configure(yscrollcommand=scrollbar_vertical.set, xscrollcommand=scrollbar_horizontal.set)

    # Entry fields and labels in a grid layout
    input_frame = ttk.Frame(tab)
    input_frame.pack(fill='x', padx=10, pady=5)
    labels = ['ID', 'Name', 'Age', 'Blood Group', 'Quantity', 'Sex', 'Registration Date', 'Phone Number']
    entries = {}
    for i, label in enumerate(labels):
        row = i // 4
        col = i % 4
        ttk.Label(input_frame, text=label + ":").grid(row=row*2, column=col*2, sticky='e')
        entry = ttk.Entry(input_frame)
        entry.grid(row=row*2, column=col*2+1, sticky='ew', padx=5, pady=2)
        entries[label.lower().replace(' ', '_')] = entry

    # Configure column weights to distribute space evenly
    for i in range(4):
        input_frame.columnconfigure(i*2+1, weight=1)

    # Buttons
    button_frame = ttk.Frame(tab)
    button_frame.pack(fill='x', pady=5)
    ttk.Button(button_frame, text="Add Entry", command=lambda: insert_recipient(
        entries['id'].get(), entries['name'].get(), entries['age'].get(),
        entries['blood_group'].get(), entries['quantity'].get(), entries['sex'].get(),
        entries['registration_date'].get(), entries['phone_number'].get(), tree
    )).pack(side='left', fill='x', expand=True)
    ttk.Button(button_frame, text="Update Selected", command=lambda: update_recipient(
        entries['id'].get(), entries['name'].get(), entries['age'].get(),
        entries['blood_group'].get(), entries['quantity'].get(), entries['sex'].get(),
        entries['registration_date'].get(), entries['phone_number'].get(), tree
    )).pack(side='left', fill='x', expand=True)
    ttk.Button(button_frame, text="Delete Selected", command=lambda: delete_recipient(
        tree.item(tree.selection(), 'values')[0], tree
    )).pack(side='left', fill='x', expand=True)

    load_recipients(tree)
    return tab


# Assuming the basic CRUD functions (insert_recipient, update_recipient, delete_recipient, load_recipients)
# are properly defined and implemented in your code.


def delete_blood_donor(bd_id, tree):
    """ Delete a blood donor from the database """
    db = connect_db()
    if db is not None:
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM Blood_Donor WHERE bd_id = %s", (bd_id,))
            db.commit()
            messagebox.showinfo('Success', 'Blood donor deleted successfully.')
            load_donors(tree)  # Refresh the list after deletion
        except psycopg2.Error as e:
            db.rollback()  # Make sure to rollback on error
            messagebox.showerror('Error', f'Failed to delete blood donor: {e}')
            print(f"SQL Error: {e}")  # Log the error to the console or a log file
        finally:
            cursor.close()
            db.close()
    else:
        messagebox.showerror('Error', 'Database connection failed.')

def update_blood_donor(bd_id, name, age, blood_group, gender, tree):
    """ Update a blood donor in the database """
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE Blood_Donor 
                SET bd_name = %s, bd_age = %s, bd_Bgroup = %s, bd_sex = %s 
                WHERE bd_id = %s
            """, (name, age, blood_group, gender, bd_id))
            db.commit()
            messagebox.showinfo('Success', 'Blood donor updated successfully.')
            load_donors(tree)  # Refresh the list after update
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', 'Failed to update blood donor: ' + str(e))
        finally:
            cursor.close()
            db.close()
def create_blood_donor_tab(tab_control):
    tab = ttk.Frame(tab_control)
    tree = ttk.Treeview(tab, columns=('ID', 'Name', 'Age', 'Blood Group', 'Gender'), show='headings')
    tree.grid(row=2, column=0, columnspan=4, sticky='nsew')
    for col in tree['columns']:
        tree.heading(col, text=col)

    # Entry setup
    entries = {'Name': ttk.Entry(tab), 'Age': ttk.Entry(tab), 'Blood Group': ttk.Entry(tab), 'Gender': ttk.Entry(tab)}
    ttk.Label(tab, text="Name:").grid(column=0, row=0)
    entries['Name'].grid(column=1, row=0)
    ttk.Label(tab, text="Age:").grid(column=0, row=1)
    entries['Age'].grid(column=1, row=1)
    ttk.Label(tab, text="Blood Group:").grid(column=2, row=0)
    entries['Blood Group'].grid(column=3, row=0)
    ttk.Label(tab, text="Gender:").grid(column=2, row=1)
    entries['Gender'].grid(column=3, row=1)

    # Function to load selected donor details into entries
    def load_selected_donor():
        selected_item = tree.selection()[0]  # Get selected item
        selected_donor = tree.item(selected_item, 'values')
        entries['Name'].delete(0, tk.END)
        entries['Name'].insert(0, selected_donor[1])
        entries['Age'].delete(0, tk.END)
        entries['Age'].insert(0, selected_donor[2])
        entries['Blood Group'].delete(0, tk.END)
        entries['Blood Group'].insert(0, selected_donor[3])
        entries['Gender'].delete(0, tk.END)
        entries['Gender'].insert(0, selected_donor[4])

    # Buttons
    ttk.Button(tab, text="Load Donor", command=load_selected_donor).grid(column=0, row=3)
    ttk.Button(tab, text="Update Donor", command=lambda: update_blood_donor(tree.item(tree.selection(), 'values')[0],
                                                                            entries['Name'].get(), entries['Age'].get(),
                                                                            entries['Blood Group'].get(), entries['Gender'].get(), tree)).grid(column=1, row=3)
    ttk.Button(tab, text="Add New Donor", command=lambda: insert_blood_donor(entries['Name'].get(), entries['Age'].get(), 
                                                                            entries['Blood Group'].get(), entries['Gender'].get(), tree)).grid(column=2, row=3)
    ttk.Button(tab, text="Delete Selected", command=lambda: delete_blood_donor(tree.item(tree.selection(), 'values')[0], tree)).grid(column=3, row=3)
    load_donors(tree)  # Load initial data
    return tab



def get_city_ids():
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("SELECT city_id FROM city")
            return [str(row[0]) for row in cursor.fetchall()]  # Cast to string for combobox
        finally:
            cursor.close()
            db.close()
    return []


def load_staff(tree):
    """ Load the staff data along with their contacts into the Treeview """
    for i in tree.get_children():
        tree.delete(i)
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("""
                SELECT rs.reco_id, rs.reco_name, sc.reco_phno
                FROM recording_staff rs
                LEFT JOIN staff_contact sc ON rs.reco_id = sc.reco_id
            """)
            for row in cursor:
                tree.insert('', 'end', values=row)
        finally:
            cursor.close()
            db.close()

def insert_staff(reco_id, reco_name, reco_phno, tree):
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO recording_staff (reco_id, reco_name)
                VALUES (%s, %s)
            """, (reco_id, reco_name))
            cursor.execute("""
                INSERT INTO staff_contact (reco_id, reco_phno)
                VALUES (%s, %s)
            """, (reco_id, reco_phno))
            db.commit()
            messagebox.showinfo('Success', 'Staff member added successfully.')
            load_staff(tree)
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', f'Failed to add staff member.\n{e}')
        finally:
            cursor.close()
            db.close()


def update_staff(reco_id, reco_name, reco_phno, tree):
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE recording_staff
                SET reco_name=%s
                WHERE reco_id=%s
            """, (reco_name, reco_id))
            cursor.execute("""
                UPDATE staff_contact
                SET reco_phno=%s
                WHERE reco_id=%s
            """, (reco_phno, reco_id))
            db.commit()
            messagebox.showinfo('Success', 'Staff member information updated successfully.')
            load_staff(tree)
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', 'Failed to update staff member information.\n{e}')
        finally:
            cursor.close()
            db.close()
def delete_staff(reco_id, tree):
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM staff_contact WHERE reco_id = %s", (reco_id,))
            cursor.execute("DELETE FROM recording_staff WHERE reco_id = %s", (reco_id,))
            db.commit()
            messagebox.showinfo('Success', 'Staff member deleted successfully.')
            load_staff(tree)
        except psycopg2.Error as e:
            db.rollback()
            messagebox.showerror('Error', 'Failed to delete staff member.\n{e}')
        finally:
            cursor.close()
            db.close()

def create_staff_management_tab(tab_control):
    tab = ttk.Frame(tab_control)

    # Configure grid for better alignment
    tab.columnconfigure(0, weight=1)
    tab.columnconfigure(1, weight=3)

    # Treeview for displaying staff data
    tree = ttk.Treeview(tab, columns=('Staff ID', 'Name', 'Phone Number'), show='headings')
    tree.grid(row=0, column=0, columnspan=2, sticky='nsew', padx=10, pady=20)
    for col in tree['columns']:
        tree.heading(col, text=col.replace('_', ' ').title())

    # Scrollbars for the Treeview
    scrollbar_vertical = ttk.Scrollbar(tab, orient='vertical', command=tree.yview)
    scrollbar_vertical.grid(row=0, column=2, sticky='ns')
    scrollbar_horizontal = ttk.Scrollbar(tab, orient='horizontal', command=tree.xview)
    scrollbar_horizontal.grid(row=1, column=0, columnspan=2, sticky='we')
    tree.configure(yscrollcommand=scrollbar_vertical.set, xscrollcommand=scrollbar_horizontal.set)

    # Entry fields for adding new staff
    labels = ['Staff ID:', 'Name:', 'Phone Number:']
    entries = {}
    for idx, label in enumerate(labels):
        ttk.Label(tab, text=label).grid(column=0, row=idx+2, padx=10, pady=5, sticky='e')
        entry = ttk.Entry(tab)
        entry.grid(column=1, row=idx+2, padx=10, pady=5, sticky='ew')
        entries[label[:-1].lower().replace(' ', '_')] = entry

    # Buttons for operations
    ttk.Button(tab, text="Add Staff", command=lambda: insert_staff(
        entries['staff_id'].get(), entries['name'].get(), entries['phone_number'].get(), tree
    )).grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

    ttk.Button(tab, text="Update Staff", command=lambda: update_staff(
        entries['staff_id'].get(), entries['name'].get(), entries['phone_number'].get(), tree
    )).grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

    ttk.Button(tab, text="Delete Staff", command=lambda: delete_staff(
        entries['staff_id'].get(), tree
    )).grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

    load_staff(tree)  # Load initial staff data

    return tab
def create_donor_search_tab(tab_control):
    tab = ttk.Frame(tab_control)
    
    # Setup for search criteria
    ttk.Label(tab, text="Search by Blood Group:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
    blood_group_entry = ttk.Entry(tab)
    blood_group_entry.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
    
    ttk.Label(tab, text="Last Donation Date (YYYY-MM-DD):").grid(row=1, column=0, padx=10, pady=10, sticky='e')
    last_donation_entry = ttk.Entry(tab)
    last_donation_entry.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
    
    ttk.Button(tab, text="Search", command=lambda: search_donors(blood_group_entry.get(), last_donation_entry.get(), tree)).grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='ew')
    
    # Treeview for displaying search results
    tree = ttk.Treeview(tab, columns=('Donor ID', 'Name', 'Blood Group', 'Last Donation Date'), show='headings')
    tree.grid(row=3, column=0, columnspan=2, sticky='nsew', padx=10, pady=10)
    tree.heading('Donor ID', text='Donor ID')
    tree.heading('Name', text='Name')
    tree.heading('Blood Group', text='Blood Group')
    tree.heading('Last Donation Date', text='Last Donation Date')
    
    return tab

def search_donors(tree, search_blood_group, last_donation_date_from=None, last_donation_date_to=None):
    """ Search donors based on blood group and date range for last donation. """
    for i in tree.get_children():
        tree.delete(i)
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            query = """
            SELECT bd_id, bd_name, bd_sex, bd_age, bd_Bgroup, bd_reg_date, next_eledgible_date
            FROM Blood_Donor
            WHERE bd_Bgroup = %s AND
                  bd_reg_date >= %s AND
                  bd_reg_date <= %s AND
                  (next_eledgible_date <= CURRENT_DATE OR next_eledgible_date IS NULL)
            """
            cursor.execute(query, (search_blood_group, last_donation_date_from, last_donation_date_to))
            for row in cursor:
                tree.insert('', 'end', values=row)
        finally:
            cursor.close()
            db.close()
def match_recipients_with_donors(tree):
    """ Match recipients with donors based on blood type. """
    for i in tree.get_children():
        tree.delete(i)
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            query = """
            SELECT r.reci_id, r.reci_name, r.reci_bgrp, d.bd_id, d.bd_name
            FROM recipient r
            JOIN Blood_Donor d ON r.reci_bgrp = d.bd_Bgroup
            WHERE d.next_eledgible_date <= CURRENT_DATE OR d.next_eledgible_date IS NULL
            ORDER BY r.reci_id
            """
            cursor.execute(query)
            for row in cursor:
                tree.insert('', 'end', values=row)
        finally:
            cursor.close()
            db.close()

def create_search_and_match_tab(tab_control):
    tab = ttk.Frame(tab_control)
    tab.pack(fill='both', expand=True)
    
    # Create Treeview to display the search results or matches
    tree = ttk.Treeview(tab, columns=('ID', 'Name', 'Blood Group', 'Donor/Recipient ID', 'Donor/Recipient Name'), show='headings')
    tree.pack(fill='both', expand=True)
    for col in tree['columns']:
        tree.heading(col, text=col)
    
    # Search area
    ttk.Label(tab, text="Blood Group:").pack(side='top', padx=10, pady=5)
    blood_group_entry = ttk.Entry(tab)
    blood_group_entry.pack(side='top', padx=10, pady=5)
    
    ttk.Label(tab, text="Eligibility Date From:").pack(side='top', padx=10, pady=5)
    date_from_entry = ttk.Entry(tab)
    date_from_entry.pack(side='top', padx=10, pady=5)
    
    ttk.Label(tab, text="Eligibility Date To:").pack(side='top', padx=10, pady=5)
    date_to_entry = ttk.Entry(tab)
    date_to_entry.pack(side='top', padx=10, pady=5)
    
    ttk.Button(tab, text="Search Donors", command=lambda: search_donors(
        tree, blood_group_entry.get(), date_from_entry.get(), date_to_entry.get()
    )).pack(side='top', padx=10, pady=10)
    
    ttk.Button(tab, text="Match Recipients", command=lambda: match_recipients_with_donors(tree)).pack(side='top', padx=10, pady=10)

    return tab

# Add this tab to your main GUI setup where you initialize `tab_control`


def match_recipients_with_donors(tree):
    """ Match recipients with donors based on blood type. """
    for i in tree.get_children():
        tree.delete(i)
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            query = """
            SELECT r.reci_id, r.reci_name, r.reci_bgrp, d.bd_id, d.bd_name
            FROM recipient r
            JOIN Blood_Donor d ON r.reci_bgrp = d.bd_Bgroup
            WHERE d.next_eledgible_date <= CURRENT_DATE OR d.next_eledgible_date IS NULL
            ORDER BY r.reci_id
            """
            cursor.execute(query)
            for row in cursor:
                tree.insert('', 'end', values=row)
        finally:
            cursor.close()
            db.close()



def create_login_window():
    login_window = tk.Tk()
    login_window.title('Login')
    login_window.geometry('300x200')

    ttk.Label(login_window, text="Select Your Role:").pack(pady=10)
    
    ttk.Button(login_window, text="Manager", command=lambda: login('Manager')).pack(fill='x', padx=50, pady=5)
    ttk.Button(login_window, text="Recording Staff", command=lambda: login('Recording Staff')).pack(fill='x', padx=50, pady=5)

    login_window.mainloop()

def create_manager_interface():
    root = tk.Tk()
    root.title("Database Management System - Manager")
    root.geometry("800x600")
    
    tab_control = ttk.Notebook(root)
    
    # Add tabs for Manager
    # Example: manager has access to all tabs
    all_tabs = [create_recipient_tab, create_diseasefinder_tab, create_blood_donor_tab,create_staff_management_tab,create_search_and_match_tab]  # Add all tab creating functions here
    for tab_func in all_tabs:
        tab = tab_func(tab_control)
        tab_control.add(tab, text=tab_func.__name__.replace('create_', '').replace('_', ' ').title())
    
    tab_control.pack(expand=1, fill="both")
    root.mainloop()

def verify_credentials(username, password, role):
    # Hardcoded credentials for demonstration
    admin_credentials = ('admin', 'adminpass')
    staff_credentials = ('staff', 'staffpass')
    
    if role == 'Manager' and (username, password) == admin_credentials:
        return True
    elif role == 'Recording Staff' and (username, password) == staff_credentials:
        return True
    else:
        return False
def create_login_window():
    login_window = tk.Tk()
    login_window.title('Login')
    login_window.geometry('300x200')

    # Entry for username
    ttk.Label(login_window, text="Username:").pack(pady=(20, 5))
    username_entry = ttk.Entry(login_window)
    username_entry.pack(pady=(0, 20))

    # Entry for password
    ttk.Label(login_window, text="Password:").pack(pady=5)
    password_entry = ttk.Entry(login_window, show='*')
    password_entry.pack(pady=(0, 20))

    # Drop-down menu for selecting the role
    role_var = tk.StringVar()
    ttk.Label(login_window, text="Select Your Role:").pack(pady=5)
    role_combobox = ttk.Combobox(login_window, textvariable=role_var, values=['Manager', 'Recording Staff'], state='readonly')
    role_combobox.pack()

    # Login button
    ttk.Button(login_window, text="Login", command=lambda: login(role_var.get(), username_entry.get(), password_entry.get(), login_window)).pack(pady=10)

    login_window.mainloop()

def login(role, username, password, window):
    if verify_credentials(username, password, role):
        window.destroy()  # Close the login window upon successful login
        if role == 'Manager':
            create_manager_interface()
        elif role == 'Recording Staff':
            create_staff_interface()
    else:
        messagebox.showerror('Login Failed', 'Invalid credentials')


def create_staff_interface():
    root = tk.Tk()
    root.title("Database Management System - Staff")
    root.geometry("800x600")
    
    tab_control = ttk.Notebook(root)
    
    # Add tabs for Recording Staff
    # Example: staff has access to limited tabs
    staff_tabs = [create_recipient_tab, create_blood_donor_tab]  # Add allowed tab creating functions here
    for tab_func in staff_tabs:
        tab = tab_func(tab_control)
        tab_control.add(tab, text=tab_func.__name__.replace('create_', '').replace('_', ' ').title())
    
    tab_control.pack(expand=1, fill="both")
    root.mainloop()
def create_real_time_dashboard(tab_control):
    tab = ttk.Frame(tab_control)
    tab.pack(fill='both', expand=True)

    # Widgets for displaying blood stock levels
    ttk.Label(tab, text="Current Blood Stock Levels", font=('Arial', 16)).pack(pady=10)
    blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    stock_levels = {blood: 50 for blood in blood_types}  # Example static data

    for blood, level in stock_levels.items():
        ttk.Label(tab, text=f"{blood}: {level} units").pack()

    # Widgets for displaying recent donations
    ttk.Label(tab, text="Recent Donations", font=('Arial', 16)).pack(pady=20)
    recent_donations = ["John Doe - A+", "Jane Smith - O-", "Alice Johnson - B+"]  # Example static data

    for donation in recent_donations:
        ttk.Label(tab, text=donation).pack()

    # Widgets for displaying upcoming appointments
    ttk.Label(tab, text="Upcoming Appointments", font=('Arial', 16)).pack(pady=20)
    upcoming_appointments = ["John Doe - April 10, 2024", "Jane Smith - April 11, 2024"]  # Example static data

    for appointment in upcoming_appointments:
        ttk.Label(tab, text=appointment).pack()

    return tab
def create_comprehensive_reporting_tab(tab_control):
    tab = ttk.Frame(tab_control)
    tab.pack(fill='both', expand=True)

    # Example static report data
    report_data = {
        "Total Donations This Month": 120,
        "Total Blood Units Used This Month": 95,
        "Donation by Blood Type": {
            "A+": 30, "A-": 10, "B+": 20, "B-": 5, "AB+": 15, "AB-": 5, "O+": 25, "O-": 10
        }
    }

    ttk.Label(tab, text="Comprehensive Reports", font=('Arial', 16)).pack(pady=10)

    for key, value in report_data.items():
        if isinstance(value, dict):
            ttk.Label(tab, text=f"{key}:", font=('Arial', 14)).pack(pady=10)
            for sub_key, sub_value in value.items():
                ttk.Label(tab, text=f"{sub_key}: {sub_value} units").pack()
        else:
            ttk.Label(tab, text=f"{key}: {value}").pack()

    return tab

def create_manager_interface():
    root = tk.Tk()
    root.title("Database Management System - Manager")
    root.geometry("800x600")

    tab_control = ttk.Notebook(root)
    reporting_tab = create_comprehensive_reporting_tab(tab_control)
    tab_control.add(reporting_tab, text='Comprehensive Reporting')

    tab_control.pack(expand=1, fill="both")
    root.mainloop()


def create_staff_interface():
    root = tk.Tk()
    root.title("Database Management System - Staff")
    root.geometry("800x600")
    
    tab_control = ttk.Notebook(root)
    
    # Define which tabs should be accessible to Recording Staff
    staff_tabs = [create_recipient_tab, create_blood_donor_tab,create_hospital_info_tab]  # Add other necessary tabs if needed
    
    # Loop through the functions to create tabs and add them to the notebook
    for tab_func in staff_tabs:
        tab = tab_func(tab_control)
        tab_control.add(tab, text=tab_func.__name__.replace('create_', '').replace('_', ' ').title())
    
    tab_control.pack(expand=1, fill="both")
    root.mainloop()

if __name__ == "__main__":
    create_login_window()  # Assuming this calls the appropriate interface based on login credentials




root = tk.Tk()
root.title("Database Management System")
root.geometry("800x600")

tab_control = ttk.Notebook(root)
blood_donor_tab = create_blood_donor_tab(tab_control)  # Make sure to define this function
blood_specimen_tab = create_blood_specimen_tab(tab_control)  # Make sure to define this function
hospital_info_tab = create_hospital_info_tab(tab_control)  # Newly added
disease_finder_tab = create_diseasefinder_tab(tab_control)
recipient_tab = create_recipient_tab(tab_control)
staff_tab = create_staff_management_tab(tab_control)
search_match = create_search_and_match_tab(tab_control)

tab_control.add(blood_donor_tab, text='Blood Donor')
tab_control.add(blood_specimen_tab, text='Blood Specimen')
tab_control.add(hospital_info_tab, text='Hospital Info')
tab_control.add(disease_finder_tab , text= 'Disease Finder Info')
tab_control.add(recipient_tab , text='Recipient Info')
tab_control.add(staff_tab , text = 'Manage staffs')
tab_control.add(search_match , text = 'search match')

tab_control.pack(expand=1, fill="both")

root.mainloop()
