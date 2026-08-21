import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ImatioApp", page_icon="🧺", layout="centered")

# Σύνδεση με το Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

def load_tab(tab_name):
    return conn.read(worksheet=tab_name, ttl=2)

st.title("🧺 ImatioApp - Διαχείριση")

# Φόρτωση Δεδομένων
df_customers = load_tab("Customers")
df_items = load_tab("Items")
df_transactions = load_tab("Transactions")

# --- 1. ΝΕΑ ΠΑΡΑΓΓΕΛΙΑ ---
with st.form("new_order_form", clear_on_submit=True):
    st.subheader("➕ Νέα Παραγγελία")
    
    # Επιλογή Πελάτη από λίστα
    customer_list = ["-- Νέος Πελάτης --"]
    if not df_customers.empty and 'Name' in df_customers.columns:
        customer_list += [f"{row['Name']} ({row['Phone']})" for _, row in df_customers.iterrows()]
    
    selected_customer = st.selectbox("Επιλογή Πελάτη", customer_list)
    
    # Αν είναι νέος πελάτης
    new_name = ""
    new_phone = ""
    if selected_customer == "-- Νέος Πελάτης --":
        new_name = st.text_input("Όνομα Νέου Πελάτη")
        new_phone = st.text_input("Τηλέφωνο Νέου Πελάτη")
    
    # Επιλογή Ειδών & Υπολογισμός
    items_desc = st.text_area("Περιγραφή / Είδη (π.χ. 2x Κοστούμια, 1x Παλτό)")
    price = st.number_input("Συνολικό Κόστος (€)", min_value=0.0, step=0.50)
    
    submit_order = st.form_submit_button("Καταχώρηση Παραγγελίας")
    
    if submit_order:
        # 1. Διαχείριση Πελάτη
        if selected_customer == "-- Νέος Πελάτης --":
            if not new_name or not new_phone:
                st.error("Συμπληρώστε όνομα και τηλέφωνο για το νέο πελάτη.")
                st.stop()
            cust_id = 1 if df_customers.empty or 'Customer_ID' not in df_customers.columns or df_customers['Customer_ID'].isnull().all() else int(df_customers['Customer_ID'].max()) + 1
            new_cust_row = pd.DataFrame([{"Customer_ID": cust_id, "Name": new_name, "Phone": new_phone, "Notes": ""}])
            df_customers = pd.concat([df_customers, new_cust_row], ignore_index=True)
            conn.update(worksheet="Customers", data=df_customers)
            cust_name_display = new_name
        else:
            cust_name_display = selected_customer.split(" (")[0]
            cust_id = df_customers[df_customers['Name'] == cust_name_display]['Customer_ID'].values[0]

        # 2. Καταχώρηση Κίνησης (Transaction)
        trans_id = 1 if df_transactions.empty or 'Transaction_ID' not in df_transactions.columns or df_transactions['Transaction_ID'].isnull().all() else int(df_transactions['Transaction_ID'].max()) + 1
        today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        new_trans_row = pd.DataFrame([{
            "Transaction_ID": trans_id,
            "Customer_ID": cust_id,
            "Items_Summary": items_desc,
            "Total_Price": price,
            "Status": "Σε αναμονή",
            "Date": today_str
        }])
        
        df_transactions = pd.concat([df_transactions, new_trans_row], ignore_index=True)
        conn.update(worksheet="Transactions", data=df_transactions)
        
        st.success(f"✅ Η παραγγελία #{trans_id} για τον/την {cust_name_display} καταχωρήθηκε!")
        st.rerun()

# --- 2. ΕΝΕΡΓΕΣ ΠΑΡΑΓΓΕΛΙΕΣ ---
st.divider()
st.subheader("📋 Ενεργές Παραγγελίες")

if not df_transactions.empty and 'Status' in df_transactions.columns:
    active_orders = df_transactions[df_transactions['Status'] != 'Παραδόθηκε']
    
    if active_orders.empty:
        st.info("Δεν υπάρχουν εκκρεμείς παραγγελίες.")
    else:
        for idx, row in active_orders.iterrows():
            cust_info = df_customers[df_customers['Customer_ID'] == row['Customer_ID']]
            c_name = cust_info['Name'].values[0] if not cust_info.empty else "Άγνωστος"
            c_phone = cust_info['Phone'].values[0] if not cust_info.empty else "-"
            
            with st.expander(f"📦 #{int(row['Transaction_ID'])} - {c_name} ({row['Status']})"):
                st.write(f"📞 **Τηλέφωνο:** {c_phone}")
                st.write(f"👕 **Είδη:** {row['Items_Summary']}")
                st.write(f"💶 **Κόστος:** {row['Total_Price']}€")
                st.write(f"📅 **Ημερομηνία:** {row['Date']}")
                
                opts = ["Σε αναμονή", "Έτοιμο", "Παραδόθηκε"]
                curr_st = row['Status']
                new_st = st.selectbox("Κατάσταση", opts, index=opts.index(curr_st) if curr_st in opts else 0, key=f"st_{row['Transaction_ID']}")
                
                if new_st != curr_st:
                    df_transactions.loc[df_transactions['Transaction_ID'] == row['Transaction_ID'], 'Status'] = new_st
                    conn.update(worksheet="Transactions", data=df_transactions)
                    st.toast(f"Ενημερώθηκε σε '{new_st}'")
                    st.rerun()
