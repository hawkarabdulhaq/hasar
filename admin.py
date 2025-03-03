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
# Page Selection
# ---------------------------
st.sidebar.title("Navigation")
page_selection = st.sidebar.selectbox("Go to:", ["Search Page", "Data Entry Page"])

# ---------------------------
# Page: SEARCH
# ---------------------------
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

# ---------------------------
# Page: DATA ENTRY
# ---------------------------
elif page_selection == "Data Entry Page":
    st.title("Data Entry & Admin Tasks")

    # Section: Upload CSV
    st.subheader("Upload CSV Data")
    table_choice = st.selectbox(
        "Select table to upload data into",
        ["Nurseries", "Trees", "Nursery_Tree_Inventory", "Search"]
    )
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        conn = get_connection()
        df.to_sql(table_choice, conn, if_exists='append', index=False)
        conn.commit()
        conn.close()
        st.success(f"Data uploaded to {table_choice} table successfully.")

    # Section: Refresh Search Table
    st.subheader("Refresh 'Search' Table")
    st.write("Refresh the 'Search' table to pull updated data from the main tables.")
    if st.button("Refresh Now"):
        refresh_search_table()
        st.success("Search table refreshed successfully.")
