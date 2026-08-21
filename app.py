import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="ImatioApp", page_icon="🧺", layout="centered")

# Scope δικαιωμάτων πρόσβασης
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource(ttl=600)
def get_gspread_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)

def load_tab(tab_name):
    client = get_gspread_client()
    sheet_url = st.secrets["spreadsheet_url"]
    sh = client.open_by_url(sheet_url)
    worksheet = sh.worksheet(tab_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data), worksheet

st.title("🧺 ImatioApp - Διαχείριση")

# Φόρτωση Δεδομένων
df_customers, ws_customers = load_tab("Customers")
df_items, ws_items = load_tab("Items")
df_transactions, ws_transactions = load_tab("Transactions")

# --- 1. ΝΕΑ ΠΑΡΑΓΓΕΛΙΑ ---
with st.form("new_order_form", clear_on_submit=True):
    st.subheader("➕ Νέα Παραγγελία")
    
    customer_list = ["-- Νέος Πελάτης --"]
    if not df_customers.empty and 'Name' in df_customers.columns:
        phone_col = 'Mobile' if 'Mobile' in df_customers.columns else 'Phone'
        customer_list += [f"{row['Name']} ({row[phone_col]})" for _, row in df_customers.iterrows() if pd.notnull(row['Name'])]
    
    selected_customer = st.selectbox("Επιλογή Πελάτη", customer_list)
    
    new_name = ""
    new_phone = ""
    if selected_customer == "-- Νέος Πελάτης --":
        new_name = st.text_input("Όνομα Νέου Πελάτη")
        new_phone = st.text_input("Τηλέφωνο Νέου Πελάτη")
    
    items_desc = st.text_area("Περιγραφή / Είδη")
    price = st.number_input("Συνολικό Κόστος (€)", min_value=0.0, step=0.50)
    
    submit_order = st.form_submit_button("Καταχώρηση Παραγγελίας")
    
    if submit_order:
        if selected_customer == "-- Νέος Πελάτης --":
            if not new_name or not new_phone:
                st.error("Συμπληρώστε όνομα και τηλέφωνο.")
                st.stop()
            
            cust_id = 1 if df_customers.empty or 'CustomerID' not in df_customers.columns else int(df_customers['CustomerID'].max()) + 1
            ws_customers.append_row([cust_id, new_name, "", "", "", new_phone, "", ""])
            cust_name_display = new_name
        else:
            cust_name_display = selected_customer.split(" (")[0]
            cust_id = int(df_customers[df_customers['Name'] == cust_name_display]['CustomerID'].values[0])

        trans_id = 1 if df_transactions.empty or 'TransactionID' not in df_transactions.columns else int(df_transactions['TransactionID'].max()) + 1
        today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        ws_transactions.append_row([trans_id, cust_id, items_desc, price, "Σε αναμονή", today_str])
        
        st.success(f"✅ Η παραγγελία #{trans_id} καταχωρήθηκε!")
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
            cust_info = df_customers[df_customers['CustomerID'] == row['CustomerID']]
            c_name = cust_info['Name'].values[0] if not cust_info.empty else "Άγνωστος"
            
            phone_val = "-"
            if not cust_info.empty:
                if 'Mobile' in cust_info.columns and pd.notnull(cust_info['Mobile'].values[0]):
                    phone_val = cust_info['Mobile'].values[0]
                elif 'Phone' in cust_info.columns and pd.notnull(cust_info['Phone'].values[0]):
                    phone_val = cust_info['Phone'].values[0]
            
            with st.expander(f"📦 #{int(row['TransactionID'])} - {c_name} ({row['Status']})"):
                st.write(f"📞 **Τηλέφωνο:** {phone_val}")
                st.write(f"👕 **Είδη:** {row['Item']}")
                st.write(f"💶 **Κόστος:** {row['TotalPrice']}€")
                st.write(f"📅 **Ημερομηνία:** {row['Date']}")
                
                opts = ["Σε αναμονή", "Έτοιμο", "Παραδόθηκε"]
                curr_st = row['Status']
                new_st = st.selectbox("Κατάσταση", opts, index=opts.index(curr_st) if curr_st in opts else 0, key=f"st_{row['TransactionID']}")
                
                if new_st != curr_st:
                    cell = ws_transactions.find(str(row['TransactionID']))
                    status_col_idx = df_transactions.columns.get_loc("Status") + 1
                    ws_transactions.update_cell(cell.row, status_col_idx, new_st)
                    st.toast(f"Ενημερώθηκε σε '{new_st}'")
                    st.rerun()
