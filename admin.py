import streamlit as st
import sqlite3
import pandas as pd

# ---------------------------
# Database Connection
# ---------------------------
def get_connection():
    """
    Returns a connection object to the SQLite database.
    """
    conn = sqlite3.connect('mydatabase.db')
    return conn

# ---------------------------
# Refresh Search Table
# ---------------------------
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
    
    # Insert new data from the joined query into 'Search' table
    df.to_sql('Search', conn, if_exists='append', index=False)
    
    conn.commit()
    conn.close()

# ---------------------------
# Page Navigation
# ---------------------------
st.sidebar.title("Navigation")
page_selection = st.sidebar.selectbox("Go to:", ["Search Page", "Data Entry Page"])

# =====================================================
# Page 1: SEARCH PAGE
# =====================================================
if page_selection == "Search Page":
    st.title("Search Trees")
    
    # Load the data from 'Search' table
    conn = get_connection()
    df_search = pd.read_sql_query("SELECT * FROM Search", conn)
    conn.close()
    
    if not df_search.empty:
        # Let user pick a tree to view details
        selected_tree = st.selectbox("Select Tree Common Name", df_search["tree_common_name"].unique())
        selected_data = df_search[df_search["tree_common_name"] == selected_tree]
        
        st.subheader("Tree Details")
        st.dataframe(selected_data)
    else:
        st.write("No data available in 'Search' table. Please add or refresh data in the 'Data Entry' page.")

# =====================================================
# Page 2: DATA ENTRY PAGE
# =====================================================
elif page_selection == "Data Entry Page":
    st.title("Data Entry & Admin Tasks")

    # ------------------------------------
    # 1. Select Table
    # ------------------------------------
    st.subheader("Select a Table")
    table_choice = st.selectbox(
        "Choose a table to manage:",
        ["Nurseries", "Trees", "Nursery_Tree_Inventory", "Search"]
    )

    # ------------------------------------
    # 2. BULK UPLOAD CSV
    # ------------------------------------
    st.subheader(f"Bulk Upload Records into '{table_choice}'")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        conn = get_connection()
        df.to_sql(table_choice, conn, if_exists='append', index=False)
        conn.commit()
        conn.close()
        st.success(f"Data uploaded to '{table_choice}' table successfully.")

    # ------------------------------------
    # 3. SINGLE DATA ENTRY
    # ------------------------------------
    st.subheader(f"Single Record Entry for '{table_choice}'")

    # Depending on the table, we present the relevant fields
    if table_choice == "Nurseries":
        with st.form("nurseries_form"):
            nursery_name = st.text_input("Nursery Name")
            address = st.text_input("Address")
            submit_nursery = st.form_submit_button("Add Nursery")
            
            if submit_nursery:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Nurseries (Nursery_name, Address)
                    VALUES (?, ?)
                """, (nursery_name, address))
                conn.commit()
                conn.close()
                st.success("Nursery record added successfully.")

    elif table_choice == "Trees":
        with st.form("trees_form"):
            common_name = st.text_input("Common Name")
            scientific_name = st.text_input("Scientific Name")
            growth_rate = st.text_input("Growth Rate")
            watering_demand = st.text_input("Watering Demand")
            shape = st.text_input("Shape")
            care_instructions = st.text_input("Care Instructions")
            main_photo_url = st.text_input("Main Photo URL")
            origin = st.text_input("Origin")
            soil_type = st.text_input("Soil Type")
            root_type = st.text_input("Root Type")
            leaf_type = st.text_input("Leaf Type")
            
            submit_tree = st.form_submit_button("Add Tree")
            
            if submit_tree:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Trees (
                        Common_name, Scientific_name, Growth_rate, Watering_demand,
                        shape, Care_instructions, Main_Photo_url, Origin,
                        Soil_type, Root_type, Leaf_Type
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    common_name, scientific_name, growth_rate, watering_demand,
                    shape, care_instructions, main_photo_url, origin,
                    soil_type, root_type, leaf_type
                ))
                conn.commit()
                conn.close()
                st.success("Tree record added successfully.")

    elif table_choice == "Nursery_Tree_Inventory":
        with st.form("nti_form"):
            nursery_name = st.text_input("Nursery Name")
            tree_common_name = st.text_input("Tree Common Name")
            quantity_in_stock = st.number_input("Quantity in Stock", min_value=0, step=1)
            min_height = st.number_input("Min Height (in cm)", min_value=0, step=1)
            max_height = st.number_input("Max Height (in cm)", min_value=0, step=1)
            packaging_type = st.text_input("Packaging Type")
            price = st.number_input("Price", min_value=0.0, step=0.01)
            
            submit_nti = st.form_submit_button("Add to Inventory")
            
            if submit_nti:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Nursery_Tree_Inventory (
                        nursery_name, tree_common_name, Quantity_in_stock,
                        Min_height, Max_height, Packaging_type, Price
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    nursery_name, tree_common_name, quantity_in_stock,
                    min_height, max_height, packaging_type, price
                ))
                conn.commit()
                conn.close()
                st.success("Inventory record added successfully.")

    elif table_choice == "Search":
        # Typically, Search is derived. But here is single data entry if needed.
        with st.form("search_form"):
            tree_common_name = st.text_input("Tree Common Name")
            quantity_in_stock = st.number_input("Quantity in Stock", min_value=0, step=1)
            min_height = st.number_input("Min Height (in cm)", min_value=0, step=1)
            max_height = st.number_input("Max Height (in cm)", min_value=0, step=1)
            packaging_type = st.text_input("Packaging Type")
            price = st.number_input("Price", min_value=0.0, step=0.01)
            scientific_name = st.text_input("Scientific Name")
            growth_rate = st.text_input("Growth Rate")
            watering_demand = st.text_input("Watering Demand")
            shape = st.text_input("Shape")
            care_instructions = st.text_input("Care Instructions")
            main_photo_url = st.text_input("Main Photo URL")
            origin = st.text_input("Origin")
            soil_type = st.text_input("Soil Type")
            root_type = st.text_input("Root Type")
            leaf_type = st.text_input("Leaf Type")
            address = st.text_input("Nursery Address")
            
            submit_search = st.form_submit_button("Add Search Record")
            
            if submit_search:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Search (
                        tree_common_name, Quantity_in_stock, Min_height, Max_height,
                        Packaging_type, Price, Scientific_name, Growth_rate,
                        Watering_demand, shape, Care_instructions, Main_Photo_url,
                        Origin, Soil_type, Root_type, Leaf_Type, Address
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tree_common_name, quantity_in_stock, min_height, max_height,
                    packaging_type, price, scientific_name, growth_rate,
                    watering_demand, shape, care_instructions, main_photo_url,
                    origin, soil_type, root_type, leaf_type, address
                ))
                conn.commit()
                conn.close()
                st.success("Record added to 'Search' table successfully.")

    # ------------------------------------
    # 4. REFRESH SEARCH TABLE
    # ------------------------------------
    st.subheader("Refresh 'Search' Table")
    st.write("Refresh the 'Search' table to pull updated data from the main tables (Nurseries, Trees, Nursery_Tree_Inventory).")
    if st.button("Refresh Now"):
        refresh_search_table()
        st.success("Search table refreshed successfully.")
