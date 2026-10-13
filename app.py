import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Εισαγωγή των αρχείων λογικής μας
import admin_egg
import admin_eidi

# --- ΡΥΘΜΙΣΗ ΣΕΛΙΔΑΣ STREAMLIT ---
st.set_page_config(
    page_title="Διαχείριση Καθαριστηρίου - Ταπητοκαθαριστηρίου",
    page_icon="🧺",
    layout="wide"
)

# --- ΣΥΝΔΕΣΗ ΜΕ GOOGLE SHEETS ---
@st.cache_resource
def init_connection():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets"
    ]
    # Διάβαστρα των credentials από τα secrets του Streamlit
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    # Άνοιγμα του Google Sheet με το όνομά του
    spreadsheet_name = "DryCleaningDB" # Βάλτε ακριβώς το όνομα του Google Sheet σας
    return client.open(spreadsheet_name)

try:
    gc = init_connection()
except Exception as e:
    st.error(f"❌ Σφάλμα σύνδεσης με το Google Sheets: {e}")
    st.stop()

# Συνάρτηση ανάκτησης φύλλου (worksheet)
def get_worksheet(sheet_name):
    return gc.worksheet(sheet_name)

# --- ΦΟΡΤΩΣΗ ΔΕΔΟΜΕΝΩΝ (Με cache για ταχύτητα) ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        df_cust = pd.DataFrame(gc.worksheet("Customers").get_all_records())
    except Exception:
        df_cust = pd.DataFrame()
        
    try:
        df_it = pd.DataFrame(gc.worksheet("Items").get_all_records())
    except Exception:
        df_it = pd.DataFrame()
        
    try:
        df_tr_items = pd.DataFrame(gc.worksheet("TrItems").get_all_records())
    except Exception:
        df_tr_items = pd.DataFrame()
        
    try:
        df_tr_xalia = pd.DataFrame(gc.worksheet("TrXalia").get_all_records())
    except Exception:
        df_tr_xalia = pd.DataFrame()
        
    return df_cust, df_it, df_tr_items, df_tr_xalia

df_customers, df_items, df_tr_items, df_tr_xalia = load_all_data()

# --- ΚΕΝΤΡΙΚΟ MENU / NAVIGATION ---
st.title("🧺 Σύστημα Διαχείρισης & Logistics Καθαριστηρίου")

tabs = st.tabs([
    "📝 Νέα Καταχώρηση", 
    "📊 Ενεργές Συναλλαγές", 
    "👥 Πελάτες", 
    "🏷️ Είδη & Τιμοκατάλογος"
])

# 1η Καρτέλα: Νέα Καταχώρηση (Φορτηγό / Μαγαζί)
with tabs[0]:
    admin_eidi.render_new_transaction_tab(
        df_customers, df_items, df_tr_items, df_tr_xalia, get_worksheet
    )

# 2η Καρτέλα: Ενεργές Συναλλαγές & Αλλαγές Κατάστασης
with tabs[1]:
    admin_eidi.render_active_transactions_tab(
        df_tr_items, df_tr_xalia, df_customers, get_worksheet
    )

# 3η Καρτέλα: Διαχείριση Πελατών
with tabs[2]:
    admin_egg.render_customers_tab(df_customers, get_worksheet)

# 4η Καρτέλα: Διαχείριση Ειδών & Τιμοκαταλόγου
with tabs[3]:
    admin_egg.render_items_tab(df_items, get_worksheet)
