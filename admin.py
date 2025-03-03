import streamlit as st
import sqlite3
import pandas as pd
from search import show_search_page  # Import the search page function

# --------------------------------
# Database connection
# --------------------------------
def get_connection():
    """
    Returns a connection object to the SQLite database.
    """
    return sqlite3.connect("mydatabase.db")

# --------------------------------
# Refresh the Search table
# --------------------------------
def refresh_search_table():
    """
    Re-populates the 'Search' table by joining data from
    Nursery_Tree_Inventory, Trees, and Nurseries.
    """
    conn = get_connection()
    query = '''
        SELECT
            nti.tree_common_name,
            nti.Quantity_in_stock,
            nti.Min_height,
            nti.Max_height,
            nti.Packaging_type,
            nti.Price,
            t.Scientific_name,
            t.Growth_rate,
            t.Watering_demand,
            t.shape,
            t.Care_instructions,
            t.Main_Photo_url,
            t.Origin,
            t.Soil_type,
            t.Root_type,
            t.Leaf_Type,
            n.Address
        FROM Nursery_Tree_Inventory nti
        LEFT JOIN Trees t
            ON nti.tree_common_name = t.Common_name
        LEFT JOIN Nurseries n
            ON nti.nursery_name = n.Nursery_name
    '''
    df = pd.read_sql_query(query, conn)
    
    # Clear existing data in 'Search' table
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Search")
    
    # Insert new data
    df.to_sql('Search', conn, if_exists='append', index=False)
    
    conn.commit()
    conn.close()

# --------------------------------
# Helper: Insert single rows
# --------------------------------
def insert_into_nurseries(Registration_code, Nursery_name, Address,
                          Contact_name, Contact_phone, Google_map_link,
                          Additional_notes):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO Nurseries
        (Registration_code, Nursery_name, Address, Contact_name,
         Contact_phone, Google_map_link, Additional_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (Registration_code, Nursery_name, Address,
                           Contact_name, Contact_phone, Google_map_link,
                           Additional_notes))
    conn.commit()
    conn.close()

def insert_into_trees(Common_name, Scientific_name, Growth_rate,
                      Watering_demand, shape, Care_instructions,
                      Main_Photo_url, Origin, Soil_type, Root_type,
                      Leaf_Type):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO Trees
        (Common_name, Scientific_name, Growth_rate, Watering_demand,
         shape, Care_instructions, Main_Photo_url, Origin, Soil_type,
         Root_type, Leaf_Type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (Common_name, Scientific_name, Growth_rate,
                           Watering_demand, shape, Care_instructions,
                           Main_Photo_url, Origin, Soil_type,
                           Root_type, Leaf_Type))
    conn.commit()
    conn.close()

def insert_into_nursery_inventory(nursery_name, tree_common_name,
                                  Quantity_in_stock, Min_height,
                                  Max_height, Packaging_type, Price):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO Nursery_Tree_Inventory
        (nursery_name, tree_common_name, Quantity_in_stock,
         Min_height, Max_height, Packaging_type, Price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (nursery_name, tree_common_name, Quantity_in_stock,
                           Min_height, Max_height, Packaging_type, Price))
    conn.commit()
    conn.close()

# --------------------------------
# Main App
# --------------------------------
st.sidebar.title("Navigation")
page_selection = st.sidebar.selectbox("Go to:", ["Search Page", "Data Entry Page"])

# ---------------------------
# PAGE 1: SEARCH PAGE
# ---------------------------
if page_selection == "Search Page":
    # Simply call the function from search.py
    show_search_page()

# ---------------------------
# PAGE 2: DATA ENTRY PAGE
# ---------------------------
elif page_selection == "Data Entry Page":
    st.title("Data Entry & Admin")

    # ------------------------------------
    # TABS for each main table
    # ------------------------------------
    tab_names = ["Nurseries", "Trees", "Nursery_Tree_Inventory"]
    tabs = st.tabs(tab_names)

    # =======================
    # 1) Nurseries Tab
    # =======================
    with tabs[0]:
        st.header("Nurseries Table")

        # -- Bulk Upload
        st.subheader("Bulk Upload CSV")
        nurseries_file = st.file_uploader("Upload CSV for Nurseries", type=["csv"])
        if nurseries_file:
            df = pd.read_csv(nurseries_file)
            conn = get_connection()
            df.to_sql("Nurseries", conn, if_exists="append", index=False)
            conn.commit()
            conn.close()
            st.success("Nurseries CSV uploaded successfully.")

        # -- Single Entry
        st.subheader("Single Entry Form")
        with st.form("nurseries_single_entry_form"):
            Registration_code = st.text_input("Registration_code")
            Nursery_name = st.text_input("Nursery_name")
            Address = st.text_input("Address")
            Contact_name = st.text_input("Contact_name")
            Contact_phone = st.text_input("Contact_phone")
            Google_map_link = st.text_input("Google_map_link")
            Additional_notes = st.text_area("Additional_notes")

            submitted = st.form_submit_button("Add Row")
            if submitted:
                insert_into_nurseries(
                    Registration_code,
                    Nursery_name,
                    Address,
                    Contact_name,
                    Contact_phone,
                    Google_map_link,
                    Additional_notes
                )
                st.success("New row added to Nurseries.")

    # =======================
    # 2) Trees Tab
    # =======================
    with tabs[1]:
        st.header("Trees Table")

        # -- Bulk Upload
        st.subheader("Bulk Upload CSV")
        trees_file = st.file_uploader("Upload CSV for Trees", type=["csv"])
        if trees_file:
            df = pd.read_csv(trees_file)
            conn = get_connection()
            df.to_sql("Trees", conn, if_exists="append", index=False)
            conn.commit()
            conn.close()
            st.success("Trees CSV uploaded successfully.")

        # -- Single Entry
        st.subheader("Single Entry Form")
        with st.form("trees_single_entry_form"):
            Common_name = st.text_input("Common_name")
            Scientific_name = st.text_input("Scientific_name")
            Growth_rate = st.number_input("Growth_rate", value=0.0)
            Watering_demand = st.text_input("Watering_demand")
            shape = st.text_input("shape")
            Care_instructions = st.text_area("Care_instructions")
            Main_Photo_url = st.text_input("Main_Photo_url")
            Origin = st.text_input("Origin")
            Soil_type = st.text_input("Soil_type")
            Root_type = st.text_input("Root_type")
            Leaf_Type = st.text_input("Leaf_Type")

            submitted_trees = st.form_submit_button("Add Row")
            if submitted_trees:
                insert_into_trees(
                    Common_name,
                    Scientific_name,
                    Growth_rate,
                    Watering_demand,
                    shape,
                    Care_instructions,
                    Main_Photo_url,
                    Origin,
                    Soil_type,
                    Root_type,
                    Leaf_Type
                )
                st.success("New row added to Trees.")

    # ================================
    # 3) Nursery_Tree_Inventory Tab
    # ================================
    with tabs[2]:
        st.header("Nursery_Tree_Inventory Table")

        # -- Bulk Upload
        st.subheader("Bulk Upload CSV")
        inventory_file = st.file_uploader("Upload CSV for Nursery_Tree_Inventory", type=["csv"])
        if inventory_file:
            df = pd.read_csv(inventory_file)
            conn = get_connection()
            df.to_sql("Nursery_Tree_Inventory", conn, if_exists="append", index=False)
            conn.commit()
            conn.close()
            st.success("Nursery_Tree_Inventory CSV uploaded successfully.")

        # -- Single Entry
        st.subheader("Single Entry Form")
        with st.form("inventory_single_entry_form"):
            # --- Fetch existing nursery names
            conn = get_connection()
            nurseries_df = pd.read_sql_query("SELECT Nursery_name FROM Nurseries", conn)
            trees_df = pd.read_sql_query("SELECT Common_name FROM Trees", conn)
            conn.close()

            nursery_options = sorted(nurseries_df["Nursery_name"].unique())
            tree_options = sorted(trees_df["Common_name"].unique())

            nursery_name = st.selectbox("nursery_name", nursery_options)
            tree_common_name = st.selectbox("tree_common_name", tree_options)

            Quantity_in_stock = st.number_input("Quantity_in_stock", value=0, step=1)
            Min_height = st.number_input("Min_height", value=0.0)
            Max_height = st.number_input("Max_height", value=0.0)
            Packaging_type = st.text_input("Packaging_type")
            Price = st.number_input("Price", value=0.0)

            submitted_inventory = st.form_submit_button("Add Row")
            if submitted_inventory:
                insert_into_nursery_inventory(
                    nursery_name,
                    tree_common_name,
                    Quantity_in_stock,
                    Min_height,
                    Max_height,
                    Packaging_type,
                    Price
                )
                st.success("New row added to Nursery_Tree_Inventory.")

    # -------------------------------
    # Refresh Search Table Button
    # -------------------------------
    st.subheader("Refresh 'Search' Table")
    st.write("Refresh the 'Search' table to pull updated data from the Nurseries, Trees, and Nursery_Tree_Inventory tables.")
    if st.button("Refresh Now"):
        refresh_search_table()
        st.success("Search table refreshed successfully.")
