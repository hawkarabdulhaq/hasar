import streamlit as st
import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect("mydatabase.db", check_same_thread=False)
c = conn.cursor()

# ----------------- Utility Functions -----------------

def run_query(query, params=None):
    if params is None:
        params = []
    c.execute(query, params)
    conn.commit()
    return c.fetchall()

def get_table_data(table):
    query = f"SELECT * FROM {table}"
    c.execute(query)
    return c.fetchall()

def insert_record(table, columns, values):
    placeholders = ','.join('?' for _ in values)
    cols = ','.join(columns)
    query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
    c.execute(query, values)
    conn.commit()

def update_record(table, pk_col, pk_val, update_cols, update_values):
    set_clause = ', '.join([f"{col} = ?" for col in update_cols])
    query = f"UPDATE {table} SET {set_clause} WHERE {pk_col} = ?"
    params = list(update_values) + [pk_val]
    c.execute(query, params)
    conn.commit()

def delete_record(table, pk_col, pk_val):
    query = f"DELETE FROM {table} WHERE {pk_col} = ?"
    c.execute(query, (pk_val,))
    conn.commit()

def update_status(email, new_status, note):
    query = "UPDATE status SET Status = ?, Note = ? WHERE Email = ?"
    c.execute(query, (new_status, note, email))
    conn.commit()

# ----------------- Mapping for Primary Keys -----------------
primary_keys = {
    "Nurseries": "nursery_id",
    "Trees": "tree_id",
    "Nursery_Tree_Inventory": "tree_inventory_id",
    "Customers": "customer_id",
    "status": "status_id"
}

# ----------------- Streamlit Admin UI -----------------

st.title("Admin Panel")
st.write("Manage and edit database tables.")

admin_menu = st.sidebar.selectbox("Admin Options", 
                                  ["View/Edit Table", "Bulk CSV Upload", "Update Order Status"])

if admin_menu == "View/Edit Table":
    table = st.selectbox("Select Table", 
                         ["Nurseries", "Trees", "Nursery_Tree_Inventory", "Customers", "status"])
    st.subheader(f"Data in {table}")
    data = get_table_data(table)
    if data:
        c.execute(f"PRAGMA table_info({table})")
        cols_info = c.fetchall()
        cols = [col[1] for col in cols_info]
        df = pd.DataFrame(data, columns=cols)
        st.dataframe(df)
    else:
        st.write("No data found in this table.")

    st.markdown("### Add a New Record")
    if table == "Nurseries":
        registration_code = st.text_input("Registration_code (example: REG123)")
        nursery_name = st.text_input("Nursery_name (example: Green Leaf Nursery)")
        address = st.text_input("Address (example: 123 Garden Lane)")
        contact_name = st.text_input("Contact_name (example: John Doe)")
        contact_phone = st.text_input("Contact_phone (example: 0123456789)")
        google_map_link = st.text_input("Google_map_link (example: https://maps.google.com/...)")
        additional_notes = st.text_input("Additional_notes")
        if st.button("Add Nursery"):
            cols_to_insert = ["Registration_code", "Nursery_name", "Address", "Contact_name", "Contact_phone", "Google_map_link", "Additional_notes"]
            values = (registration_code, nursery_name, address, contact_name, contact_phone, google_map_link, additional_notes)
            insert_record("Nurseries", cols_to_insert, values)
            st.success("Nursery record added successfully!")

    elif table == "Trees":
        common_name = st.text_input("Common_name (example: Oak)")
        scientific_name = st.text_input("Scientific_name (example: Quercus)")
        growth_rate = st.number_input("Growth_rate (Cm/yr)", value=10)
        watering_demand = st.text_input("Watering_demand (example: Moderate)")
        shape = st.text_input("Shape (example: Spherical)")
        care_instructions = st.text_input("Care_instructions (example: Prune annually)")
        main_photo_url = st.text_input("Main_Photo_url (example: https://example.com/photo.jpg)")
        origin = st.text_input("Origin (example: North America)")
        soil_type = st.text_input("Soil_type (example: Loamy)")
        root_type = st.text_input("Root_type (example: Deep)")
        leaf_type = st.text_input("Leaf Type (example: Deciduous)")
        if st.button("Add Tree"):
            cols_to_insert = ["Common_name", "Scientific_name", "Growth_rate", "Watering_demand", "shape", 
                              "Care_instructions", "Main_Photo_url", "Origin", "Soil_type", "Root_type", '"Leaf Type"']
            values = (common_name, scientific_name, growth_rate, watering_demand, shape, care_instructions, 
                      main_photo_url, origin, soil_type, root_type, leaf_type)
            insert_record("Trees", cols_to_insert, values)
            st.success("Tree record added successfully!")

    elif table == "Nursery_Tree_Inventory":
        nursery_id = st.number_input("nursery_id (example: 1)", value=1, step=1)
        tree_id = st.number_input("tree_id (example: 1)", value=1, step=1)
        quantity_in_stock = st.number_input("Quantity_in_stock", value=100, step=1)
        min_height = st.number_input("Min_height (example: 50)", value=50)
        max_height = st.number_input("Max_height (example: 200)", value=200)
        packaging_type = st.text_input("Packaging_type (example: Potted)")
        planting = st.selectbox("Planting", ["Yes", "No"])
        price = st.number_input("Price (IQD)", value=50000)
        if st.button("Add Nursery Tree Inventory"):
            cols_to_insert = ["nursery_id", "tree_id", "Quantity_in_stock", "Min_height", "Max_height", "Packaging_type", "Planting", "Price"]
            values = (nursery_id, tree_id, quantity_in_stock, min_height, max_height, packaging_type, planting, price)
            insert_record("Nursery_Tree_Inventory", cols_to_insert, values)
            st.success("Nursery Tree Inventory record added!")

    elif table == "Customers":
        quantity = st.number_input("Quantity", value=1, step=1)
        username = st.text_input("Username (example: user123)")
        customer_full_name = st.text_input("Customer_full_Name (example: Jane Doe)")
        address = st.text_input("Address (example: 456 Elm Street)")
        whatsapp_number = st.text_input("Whatsapp Number (example: +1234567890)")
        email = st.text_input("Email (example: jane@example.com)")
        price_val = st.number_input("Price", value=50000)
        payment_preferences = st.text_input("Payment Preferences (example: Bank Transfer)")
        if st.button("Add Customer"):
            cols_to_insert = ["Quantity", "Username", "Customer_full_Name", "Address", '"Whatsapp Number"', "Email", "price", '"Payment Preferences"']
            values = (quantity, username, customer_full_name, address, whatsapp_number, email, price_val, payment_preferences)
            insert_record("Customers", cols_to_insert, values)
            st.success("Customer record added!")

    elif table == "status":
        username = st.text_input("Username (example: user123)")
        email = st.text_input("Email (example: jane@example.com)")
        status_val = st.text_input("Status (example: Order Placed)")
        note = st.text_area("Note (example: Please deliver in the morning)")
        if st.button("Add Status Record"):
            cols_to_insert = ["Username", "Email", "Status", "Note"]
            values = (username, email, status_val, note)
            insert_record("status", cols_to_insert, values)
            st.success("Status record added!")

    st.markdown("### Edit/Delete Record")
    with st.expander("Edit/Delete Record"):
        # Use the mapping for the primary key column name
        pk_col = primary_keys[table]
        # Retrieve fresh table data for selection
        data = get_table_data(table)
        if data:
            # Build a dictionary mapping primary key to record data
            options = {str(row[0]): row for row in data}
            selected_pk = st.selectbox(f"Select {pk_col} to Edit/Delete", list(options.keys()))
            record = options[selected_pk]
            
            # Get column names for this table
            c.execute(f"PRAGMA table_info({table})")
            cols_info = c.fetchall()
            cols = [col[1] for col in cols_info]
            
            # Create a form pre-filled with the current record values
            st.write("Modify the fields below and click Update. To delete, click Delete Record.")
            updated_values = {}
            for i, col in enumerate(cols):
                # Skip primary key field from editing
                if col == pk_col:
                    st.write(f"**{col}:** {record[i]}")
                else:
                    updated_values[col] = st.text_input(col, value=str(record[i]))
            
            col_names = [col for col in cols if col != pk_col]
            if st.button("Update Record"):
                # Update the record using the updated values (order should match col_names)
                update_vals = [updated_values[col] for col in col_names]
                update_record(table, pk_col, selected_pk, col_names, update_vals)
                st.success("Record updated successfully!")
            if st.button("Delete Record"):
                delete_record(table, pk_col, selected_pk)
                st.success("Record deleted successfully!")
        else:
            st.info("No records available for editing or deletion.")

elif admin_menu == "Bulk CSV Upload":
    st.subheader("Bulk CSV Upload")
    table = st.selectbox("Select Table for CSV Upload", 
                         ["Nurseries", "Trees", "Nursery_Tree_Inventory", "Customers", "status"])
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.write("Preview of uploaded data:")
            st.dataframe(df)
            if st.button("Upload Data"):
                df.to_sql(table, conn, if_exists="append", index=False)
                st.success("Data uploaded successfully!")
        except Exception as e:
            st.error(f"Error uploading CSV: {e}")

elif admin_menu == "Update Order Status":
    st.subheader("Update Order Status")
    email_input = st.text_input("Enter Customer Email (example: jane@example.com)")
    new_status = st.selectbox("Select New Status", 
                              ["Order Placed", "Order Confirmed", "Order Processing", "Packaging", "In Transit", "Delivered", "Canceled"])
    note = st.text_area("Enter Note (optional)")
    if st.button("Update Status"):
        update_status(email_input, new_status, note)
        st.success("Order status updated!")


