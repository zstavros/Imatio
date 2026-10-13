import streamlit as st
import pandas as pd
import gspread
import base64
from google.oauth2.service_account import Credentials

# Εισαγωγή των υπόλοιπων αρχείων λογικής
import admin_egg
import admin_eidi
import admin_fast

# --- ΡΥΘΜΙΣΗ ΣΕΛΙΔΑΣ STREAMLIT ---
st.set_page_config(
    page_title="IMATIO ΣΤΕΓΝΟΚΑΘΑΡΙΣΤΗΡΙΑ",
    page_icon="🧺",
    layout="wide"
)

# --- CSS ΓΙΑ ΑΦΑΙΡΕΣΗ ΚΕΝΟΥ ΚΑΙ ΔΙΑΜΟΡΦΩΣΗ ΕΠΙΚΕΦΑΛΙΔΑΣ ---
hide_streamlit_style = """
    <style>
    /* Απόκρυψη στοιχείων Streamlit */
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    .stAppFooter {display: none !important;}
    
    /* Μηδενισμός περιθωρίων στην κορυφή */
    .block-container {
        padding-top: 0.5rem !important;
        margin-top: 0rem !important;
    }
    header {
        visibility: hidden !important;
        height: 0px !important;
    }
    
    /* Διαμόρφωση επικεφαλίδας με λογότυπο */
    .header-container {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 1rem;
    }
    .header-title {
        font-size: 1.6rem !important;
        font-weight: 700;
        color: #1E1E1E;
        margin: 0;
        line-height: 1.2;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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
    
    if "spreadsheet_url" in st.secrets:
        return client.open_by_url(st.secrets["spreadsheet_url"])
    elif "spreadsheet_id" in st.secrets:
        return client.open_by_key(st.secrets["spreadsheet_id"])
    else:
        return client.open("ImatioDB")

try:
    gc = init_connection()
except Exception as e:
    st.error(f"❌ Σφάλμα σύνδεσης με το Google Sheets: {e}")
    st.stop()

# CACHE ΤΩΝ WORKSHEETS ΓΙΑ ΝΑ ΜΗΝ ΧΤΥΠΑΕΙ ΤΟ GOOGLE API RATE LIMIT!
@st.cache_resource
def get_worksheet(sheet_name):
    return gc.worksheet(sheet_name)
    
# Συνάρτηση ανάκτησης φύλλου (worksheet)
def get_worksheet(sheet_name):
    return gc.worksheet(sheet_name)

# --- ΦΟΡΤΩΣΗ ΔΕΔΟΜΕΝΩΝ ---
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

# --- ΕΜΦΑΝΙΣΗ ΛΟΓΟΤΥΠΟΥ ΚΑΙ ΕΠΙΚΕΦΑΛΙΔΑΣ ---
def render_custom_header():
    try:
        with open("logo.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        img_html = f'<img src="data:image/png;base64,{encoded_string}" width="65" height="65" style="border-radius: 50%; object-fit: cover;">'
    except Exception:
        img_html = '🧺'

    st.markdown(
        f'''
        <div class="header-container">
            {img_html}
            <h1 class="header-title">IMATIO ΣΤΕΓΝΟΚΑΘΑΡΙΣΤΗΡΙΑ</h1>
        </div>
        ''',
        unsafe_allow_html=True
    )

render_custom_header()

# --- ΚΕΝΤΡΙΚΟ MENU / NAVIGATION ---
tabs = st.tabs([
    "🚛 Γρήγορη Φόρτωση", 
    "📝 Νέα Καταχώρηση", 
    "📊 Ενεργές Συναλλαγές", 
    "👥 Πελάτες", 
    "🏷️ Είδη & Τιμοκατάλογος"
])

# 1η Καρτέλα: Γρήγορη Φόρτωση
with tabs[0]:
    admin_fast.render_fast_loading_tab(df_customers, df_items, get_worksheet)

# 2η Καρτέλα: Νέα Καταχώρηση
with tabs[1]:
    admin_eidi.render_new_transaction_tab(
        df_customers, df_items, df_tr_items, df_tr_xalia, get_worksheet
    )

# 3η Καρτέλα: Ενεργές Συναλλαγές
with tabs[2]:
    admin_eidi.render_active_transactions_tab(
        df_tr_items, df_tr_xalia, df_customers, get_worksheet
    )

# 4η Καρτέλα: Πελάτες
with tabs[3]:
    admin_egg.render_customers_tab(df_customers, get_worksheet)

# 5η Καρτέλα: Είδη
with tabs[4]:
    admin_egg.render_items_tab(df_items, get_worksheet)
