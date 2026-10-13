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
    page_title="Imatio",
    page_icon="🧺",
    layout="wide"
)

# --- CSS GIA AFALRESI KENOU APO THN KORYFH ---
hide_streamlit_style = """
    <style>
    /* Apokrypsi stoicheion Streamlit */
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    .stAppFooter {display: none !important;}
    
    /* Midenismos perithorion stin koryfi gia na anevei terma pano */
    .block-container {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    header {
        visibility: hidden !important;
        height: 0px !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- SYNDESI ME GOOGLE SHEETS ---
@st.cache_resource
def init_connection():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    if "spreadsheet_url" in st.secrets:
        return client.open_by_url(st.secrets["spreadsheet_url"])
    elif "spreadsheet_id" in st.secrets:
        return client.open_by_key(st.secrets["spreadsheet_id"])
    else:
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

# 1i Kartela: Grigori Fortosi
with tabs[0]:
    admin_fast.render_fast_loading_tab(df_customers, df_items, get_worksheet)

# 2i Kartela: Nea Katachorisi
with tabs[1]:
    admin_eidi.render_new_transaction_tab(
        df_customers, df_items, df_tr_items, df_tr_xalia, get_worksheet
    )

# 3i Kartela: Energes Synallages
with tabs[2]:
    admin_eidi.render_active_transactions_tab(
        df_tr_items, df_tr_xalia, df_customers, get_worksheet
    )

# 4i Kartela: Pelates
with tabs[3]:
    admin_egg.render_customers_tab(df_customers, get_worksheet)

# 5i Kartela: Eidi
with tabs[4]:
    admin_egg.render_items_tab(df_items, get_worksheet)
