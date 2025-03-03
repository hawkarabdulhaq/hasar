import streamlit as st
import sqlite3
import pandas as pd


# Function to connect to the SQLite database
def get_connection():
    conn = sqlite3.connect('mydatabase.db')
    return conn


# Function to refresh the Search table by joining data from Nursery_Tree_Inventory, Trees, and Nurseries.
def refresh_search_table():
    conn = get_connection()
    query = '''
    SELECT nti.tree_common_name,
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
    LEFT JOIN Trees t ON nti.tree_common_name = t.Common_name
    LEFT JOIN Nurseries n ON nti.nursery_name = n.Nursery_name
    '''
    df = pd.read_sql_query(query, conn)
    # Clear the current data in Search table
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Search")
    # Insert the new joined data into the Search table
    df.to_sql('Search', conn, if_exists='append', index=False)
    conn.commit()
    conn.close()


# ---------------------------
# Sidebar: Admin Panel
# ---------------------------
st.sidebar.title("Admin Panel")
admin_option = st.sidebar.selectbox("Select admin function", ["", "Upload CSV Data", "Refresh Search Table"])


if admin_option == "Upload CSV Data":
    table_choice = st.sidebar.selectbox("Select table", ["Nurseries", "Trees", "Nursery_Tree_Inventory", "Search"])
    uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        conn = get_connection()
        df.to_sql(table_choice, conn, if_exists='append', index=False)
        conn.commit()
        conn.close()
        st.sidebar.success(f"Data uploaded to {table_choice} table successfully.")


if admin_option == "Refresh Search Table":
    if st.sidebar.button("Refresh Now"):
        refresh_search_table()
        st.sidebar.success("Search table refreshed successfully.")


# ---------------------------
# Main App: Search Functionality
# ---------------------------
st.title("Search Trees")


# Load the Search table data
conn = get_connection()
df_search = pd.read_sql_query("SELECT * FROM Search", conn)
conn.close()


if not df_search.empty:
    # Dropdown for tree common name from Search table
    selected_tree = st.selectbox("Select Tree Common Name", df_search["tree_common_name"].unique())
    # Show details for the selected tree
    selected_data = df_search[df_search["tree_common_name"] == selected_tree]
    st.write("Details:")
    st.dataframe(selected_data)
else:
    st.write("No data available in Search table.")
