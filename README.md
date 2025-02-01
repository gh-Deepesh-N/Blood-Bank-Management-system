# Blood Bank Management System

The **Blood Bank Management System** is a Python-based application designed to enhance the efficiency and reliability of blood bank operations, ensuring robust tracking of blood inventory, donor records, and recipient details.

## Installation

Ensure you have PostgreSQL installed and running on your system. Then, clone the repository and run the Python application:

```bash
# Clone the repository
git clone https://github.com/your-username/blood-bank-management.git
cd blood-bank-management

# Run the application
python blood_bank_system.py


## Usage

### Login Page
![Login Page](https://github.com/user-attachments/assets/ec244924-2f00-466f-a91f-5b39c5ab1a85)
*Fig 7.2.1 login page*

### Donor Management Interface
![Donor Management](https://github.com/user-attachments/assets/placeholder-for-image.png)
*Fig 7.3 Donor Management Interface*

```python
# Connect to the database
def connect_db():
    # Establish connection with PostgreSQL
    pass

# Add a new blood donor
insert_blood_donor(name="John Doe", age=30, blood_group="O+", gender="M", tree=tree_view)

# Delete an existing donor
delete_blood_donor(bd_id=101, tree=tree_view)

# Load all donor records
load_donors(tree=tree_view)


