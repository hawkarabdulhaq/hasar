import streamlit as st
import sqlite3
import pandas as pd

def get_connection():
    """
    Returns a connection object to the SQLite database.
    """
    return sqlite3.connect("mydatabase.db")

def show_search_page():
    """
    Displays the Search Page in Streamlit.
    """
    st.title("Search Trees")
    
    # Read data from 'Search' table
    conn = get_connection()
    df_search = pd.read_sql_query("SELECT * FROM Search", conn)
    conn.close()
    
    # If 'Search' table is empty, instruct user to add data
    if df_search.empty:
        st.write("No data in 'Search' table. Please go to 'Data Entry Page' to add or refresh.")
        return

    # Otherwise, allow selecting a tree from the 'tree_common_name' column
    selected_tree = st.selectbox("Select Tree Common Name",
                                 df_search["tree_common_name"].unique())
    selected_data = df_search[df_search["tree_common_name"] == selected_tree]

    st.subheader("Tree Details")
    st.dataframe(selected_data)
