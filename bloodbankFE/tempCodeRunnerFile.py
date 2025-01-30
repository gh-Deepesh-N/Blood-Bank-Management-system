def create_blood_donor_tab(tab_control):
    tab = ttk.Frame(tab_control)
    
    # Treeview setup
    tree = ttk.Treeview(tab, columns=('ID', 'Name', 'Age', 'Blood Group', 'Gender'), show='headings')
    tree.grid(row=2, column=0, columnspan=4, sticky='nsew')
    tree.heading('ID', text='ID')
    tree.heading('Name', text='Name')
    tree.heading('Age', text='Age')
    tree.heading('Blood Group', text='Blood Group')
    tree.heading('Gender', text='Gender')

    # Entry setup
    ttk.Label(tab, text="Name:").grid(column=0, row=0)
    ttk.Label(tab, text="Age:").grid(column=0, row=1)
    ttk.Label(tab, text="Blood Group:").grid(column=2, row=0)
    ttk.Label(tab, text="Gender:").grid(column=2, row=1)

    name_entry = ttk.Entry(tab)
    age_entry = ttk.Entry(tab)
    blood_group_entry = ttk.Entry(tab)
    gender_entry = ttk.Entry(tab)

    name_entry.grid(column=1, row=0)
    age_entry.grid(column=1, row=1)
    blood_group_entry.grid(column=3, row=0)
    gender_entry.grid(column=3, row=1)

    # Buttons
    ttk.Button(tab, text="Add New Donor", command=lambda: insert_blood_donor(name_entry.get(), age_entry.get(), blood_group_entry.get(), gender_entry.get(), tree)).grid(column=0, row=3)
    ttk.Button(tab, text="Refresh List", command=lambda: load_donors(tree)).grid(column=1, row=3)
    ttk.Button(tab, text="Delete Selected", command=lambda: delete_blood_donor(tree.item(tree.selection(), 'values')[0], tree)).grid(column=2, row=3)

    load_donors(tree)  # Load initial data

    return tab