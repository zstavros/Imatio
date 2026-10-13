import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Εισαγωγή όλων των αρχείων λογικής μας
import admin_egg
import admin_eidi
import admin_fast

# --- ΡΥΘΜΙΣΗ ΣΕΛΙΔΑΣ STREAMLIT ---
st.set_page_config(
    page_title="Διαχείριση Καθαριστηρίου - Ταπητοκαθαριστηρίου",
    page_icon="🧺",
    layout="wide"
)

# Αντικαταστήστε με το δικό σας Google Sheet ID αν προτιμάτε open_by_key, 
# ή κρατήστε το client.open αν χρησιμοποιείτε το όνομα αρχείου (με ενεργοποιημένο Drive API).
SPREADSHEET_ID = "ΒΑΛΕ_ΕΔΩ_TO_ID_TOY_GOOGLE_SHEET_ΣΟΥ"

# --- ΣΥΝΔΕΣΗ ΜΕ GOOGLE SHEETS ---
@st.cache_resource
def init_connection():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    # Επιλέξτε ανάλογα με το πώς συνδέεστε (με ID ή με Όνομα):
    return client.open_by_key(SPREADSHEET_ID)
    # Ή αν προτιμάτε με όνομα αρχείου:
    # return client.open("DryCleaningDB")

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
    "🚛 Γρήγορη Φόρτωση",
    "📝 Νέα Καταχώρηση", 
    "📊 Ενεργές Συναλλαγές", 
    "👥 Πελάτες", 
    "🏷️ Είδη & Τιμοκατάλογος"
])

# 1η Καρτέλα: Γρήγορη Μαζική Φόρτωση (admin_fast.py)
with tabs[0]:
    admin_fast.render_fast_loading_tab(df_customers, df_items, get_worksheet)

# 2η Καρτέλα: Νέα Καταχώρηση (admin_eidi.py)
with tabs[1]:
    admin_eidi.render_new_transaction_tab(
        df_customers, df_items, df_tr_items, df_tr_xalia, get_worksheet
    )

# 3η Καρτέλα: Ενεργές Συναλλαγές (admin_eidi.py)
with tabs[2]:
    admin_eidi.render_active_transactions_tab(
        df_tr_items, df_tr_xalia, df_customers, get_worksheet
    )

# 4η Καρτέλα: Διαχείριση Πελατών (admin_egg.py)
with tabs[3]:
    admin_egg.render_customers_tab(df_customers, get_worksheet)

# 5η Καρτέλα: Διαχείριση Ειδών & Τιμοκαταλόγου (admin_egg.py)
with tabs[4]:
    admin_egg.render_items_tab(df_items, get_worksheet)
