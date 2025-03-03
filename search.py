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
    Displays the Search Page in Streamlit,
    allowing users to filter on several fields.
    """
    st.title("Search Trees")
    
    # --- Read all data from the 'Search' table
    conn = get_connection()
    df_search = pd.read_sql_query("SELECT * FROM Search", conn)
    conn.close()

    # If the table is empty, inform the user
    if df_search.empty:
        st.write("No data in 'Search' table. Please go to 'Data Entry Page' to add or refresh.")
        return

    # ----------------------
    # Filter Widgets
    # ----------------------
    # 1) Tree Name
    tree_options = sorted(df_search["tree_common_name"].dropna().unique())
    tree_choice = st.selectbox("Tree Name", ["All"] + tree_options)

    # 2) Min Height & Max Height
    #    - We'll let the user specify numeric values for filtering
    min_height_input = st.number_input("Minimum Height (m)", value=0.0, step=0.1)
    max_height_input = st.number_input("Maximum Height (m)", value=1000.0, step=0.1)

    # 3) Packaging Type
    packaging_options = sorted(df_search["Packaging_type"].dropna().unique())
    packaging_choice = st.selectbox("Packaging Type", ["All"] + packaging_options)

    # 4) Growth Rate
    #    - If you want an exact match, you can do so with a numeric input.
    #    - Alternatively, you might want to store a range or do ">= growth_rate", etc.
    growth_rate_input = st.number_input("Growth Rate (exact match)", value=0.0, step=0.1)

    # 5) Shape
    shape_options = sorted(df_search["shape"].dropna().unique())
    shape_choice = st.selectbox("Shape", ["All"] + shape_options)

    # ----------------------
    # Filtering the Data
    # ----------------------
    df_filtered = df_search.copy()

    # Tree Name filter
    if tree_choice != "All":
        df_filtered = df_filtered[df_filtered["tree_common_name"] == tree_choice]

    # Min/Max Height filter
    df_filtered = df_filtered[df_filtered["Min_height"] >= min_height_input]
    df_filtered = df_filtered[df_filtered["Max_height"] <= max_height_input]

    # Packaging Type filter
    if packaging_choice != "All":
        df_filtered = df_filtered[df_filtered["Packaging_type"] == packaging_choice]

    # Growth Rate filter
    # If growth_rate_input is > 0, we'll filter for an exact match
    # Adjust logic if you prefer a range-based filter
    if growth_rate_input > 0:
        df_filtered = df_filtered[df_filtered["Growth_rate"] == growth_rate_input]

    # Shape filter
    if shape_choice != "All":
        df_filtered = df_filtered[df_filtered["shape"] == shape_choice]

    # ----------------------
    # Display Results
    # ----------------------
    st.subheader("Search Results")
    st.write(f"Showing {len(df_filtered)} result(s):")
    st.dataframe(df_filtered)
