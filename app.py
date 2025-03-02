import streamlit as st
import sqlite3


# Connect to the SQLite database
conn = sqlite3.connect("mydatabase.db", check_same_thread=False)
c = conn.cursor()


# ---------- Database Functions ----------


def search_tree(search_query):
    query = """
        SELECT t.tree_id, t.Common_name, t.Scientific_name, t.Growth_rate,
               t.Watering_demand, t.shape, t.Care_instructions, t.Main_Photo_url,
               t.Origin, t.Soil_type, t.Root_type, t."Leaf Type",
               nti.Price, nti.Packaging_type, nti.Planting, nti.Quantity_in_stock
        FROM Trees t
        JOIN Nursery_Tree_Inventory nti ON t.tree_id = nti.tree_id
        WHERE t.Common_name LIKE ? OR t.Scientific_name LIKE ?
    """
    param = f"%{search_query}%"
    c.execute(query, (param, param))
    return c.fetchone()


def insert_customer(data):
    query = """
        INSERT INTO Customers (Quantity, Username, Customer_full_Name, Address, "Whatsapp Number", Email, price, "Payment Preferences")
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    c.execute(query, data)
    conn.commit()


def insert_status(username, email):
    query = """
        INSERT INTO status (Username, Email, Status, Note)
        VALUES (?, ?, ?, ?)
    """
    c.execute(query, (username, email, "Order Placed", ""))
    conn.commit()


def get_order_status(email):
    query = "SELECT Username, Email, Status, Note FROM status WHERE Email = ?"
    c.execute(query, (email,))
    return c.fetchall()


# ---------- Session State Initialization ----------
if 'purchase_clicked' not in st.session_state:
    st.session_state.purchase_clicked = False
if 'tree_details' not in st.session_state:
    st.session_state.tree_details = None
if 'page' not in st.session_state:
    st.session_state.page = "Nursery"


# ---------- Sidebar as Buttons ----------
st.sidebar.markdown("## Navigate to Nursery")
if st.sidebar.button("Nursery"):
    st.session_state.page = "Nursery"
if st.sidebar.button("Order Status"):
    st.session_state.page = "Order Status"


# ---------- Streamlit App UI ----------


if st.session_state.page == "Nursery":
    st.title("Evergreen Nursery & Tree Solutions")
    st.header("Explore Our Premium Selections")
   
    if not st.session_state.purchase_clicked:
        # Updated search engine prompt
        search_query = st.text_input("Find Your Ideal Tree (by Common or Scientific Name):")
        if st.button("Search"):
            result = search_tree(search_query)
            if result:
                st.session_state.tree_details = {
                    "tree_id": result[0],
                    "common_name": result[1],
                    "scientific_name": result[2],
                    "growth_rate": result[3],
                    "watering_demand": result[4],
                    "shape": result[5],
                    "care_instructions": result[6],
                    "main_photo_url": result[7],
                    "origin": result[8],
                    "soil_type": result[9],
                    "root_type": result[10],
                    "leaf_type": result[11],
                    "price": result[12],
                    "packaging_type": result[13],
                    "planting": result[14],
                    "available_quantity": result[15]
                }
            else:
                st.warning("No tree found with that search criteria.")


        if st.session_state.tree_details is not None:
            details = st.session_state.tree_details
            st.subheader("Tree Details")
            st.write("**Common Name:**", details["common_name"])
            st.write("**Scientific Name:**", details["scientific_name"])
            st.write("**Growth Rate (Cm/yr):**", details["growth_rate"])
            st.write("**Watering Demand:**", details["watering_demand"])
            st.write("**Shape:**", details["shape"])
            st.write("**Care Instructions:**", details["care_instructions"])
            st.write("**Main Photo URL:**", details["main_photo_url"])
            st.write("**Origin:**", details["origin"])
            st.write("**Soil Type:**", details["soil_type"])
            st.write("**Root Type:**", details["root_type"])
            st.write("**Leaf Type:**", details["leaf_type"])
            st.write("**Price (IQD):**", details["price"])
            st.write("**Packaging Type:**", details["packaging_type"])
            st.write("**Planting:**", details["planting"])
            st.write("**Available Quantity:**", details["available_quantity"])


            if st.button("Purchase"):
                st.session_state.purchase_clicked = True


    if st.session_state.purchase_clicked:
        details = st.session_state.tree_details
        st.subheader("Purchase Form")
        st.write("You selected:", details["common_name"], "-", details["scientific_name"])
        quantity = st.number_input("Quantity", min_value=1, max_value=details["available_quantity"], value=1, step=1)
        total_price = details["price"] * quantity
        st.write("**Total Price (IQD):**", total_price)
        username = st.text_input("Username")
        customer_full_name = st.text_input("Customer Full Name")
        address = st.text_area("Address")
        whatsapp_number = st.text_input("Whatsapp Number")
        email = st.text_input("Email")
        payment_preferences = st.selectbox("Payment Preferences", ["Credit Card", "Bank Transfer", "Cash on Delivery"])
       
        if st.button("Order"):
            customer_data = (quantity, username, customer_full_name, address, whatsapp_number, email, total_price, payment_preferences)
            insert_customer(customer_data)
            insert_status(username, email)
            st.success("Order placed successfully!")
            st.session_state.purchase_clicked = False
            st.session_state.tree_details = None


elif st.session_state.page == "Order Status":
    st.title("Order Status")
    st.write("Enter your email to check the status of your order.")
    email_status = st.text_input("Email for Order Status")
    if st.button("Check Status"):
        orders = get_order_status(email_status)
        if orders:
            for order in orders:
                st.write("**Username:**", order[0])
                st.write("**Email:**", order[1])
                st.write("**Status:**", order[2])
                st.write("**Note:**", order[3])
                st.markdown("---")
        else:
            st.info("No orders found for this email.")


