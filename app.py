import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Eisagogi ton ypoloipon archeion logikis
import admin_egg
import admin_eidi
import admin_fast

# --- RHYTHMISI SELIDAS STREAMLIT ---
st.set_page_config(
    page_title="ImatioApp - Diacheirisi Katharistiriou",
    page_icon="🧺",
    layout="wide"
)

# --- SYNDESI ME GOOGLE SHEETS (Apeutheias apo Secrets) ---
@st.cache_resource
def init_connection():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    # Diavazei apeutheias to URL apo ta Secrets (st.secrets["spreadsheet_url"])
    # h an echeis orisei to ID sta secrets: st.secrets["spreadsheet_id"]
    if "spreadsheet_url" in st.secrets:
        return client.open_by_url(st.secrets["spreadsheet_url"])
    elif "spreadsheet_id" in st.secrets:
        return client.open_by_key(st.secrets["spreadsheet_id"])
    else:
        # Fallback στο όνομα του αρχείου ImatioDB
        return client.open("ImatioDB")

try:
    gc = init_connection()
except Exception as e:
    st.error(f"❌ Sfalma syndesis me to Google Sheets: {e}")
    st.stop()

# Synartisi anaktisis fyllou (worksheet)
def get_worksheet(sheet_name):
    return gc.worksheet(sheet_name)

# --- FORTOSI DEDOMENON ---
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

# --- KENTRIKO MENU / NAVIGATION ---
st.title("🧺 ImatioApp - Logistics & Diacheirisi")

tabs = st.tabs([
    "🚛 Grigori Fortosi", 
    "📝 Nea Katachorisi", 
    "📊 Energes Synallages", 
    "👥 Pelates", 
    "🏷️ Eidi & Timokatalogos"
])

# 1i Kartela: Grigori Fortosi (admin_fast.py)
with tabs[0]:
    admin_fast.render_fast_loading_tab(df_customers, df_items, get_worksheet)

# 2i Kartela: Nea Katachorisi (admin_eidi.py)
with tabs[1]:
    admin_eidi.render_new_transaction_tab(
        df_customers, df_items, df_tr_items, df_tr_xalia, get_worksheet
    )

# 3i Kartela: Energes Synallages (admin_eidi.py)
with tabs[2]:
    admin_eidi.render_active_transactions_tab(
        df_tr_items, df_tr_xalia, df_customers, get_worksheet
    )

# 4i Kartela: Pelates (admin_egg.py)
with tabs[3]:
    admin_egg.render_customers_tab(df_customers, get_worksheet)

# 5i Kartela: Eidi (admin_egg.py)
with tabs[4]:
    admin_egg.render_items_tab(df_items, get_worksheet)
