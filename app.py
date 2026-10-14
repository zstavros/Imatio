import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import base64

import admin_fast
import admin_eidi

st.set_page_config(page_title="IMATIO", layout="wide", initial_sidebar_state="collapsed")

# --- ΑΥΣΤΗΡΟ (STRICT) CUSTOM STYLING ΓΙΑ ΣΤΑΘΕΡΕΣ ΔΙΑΣΤΑΣΕΙΣ ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 3.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 1200px;
        }

        /* Header Bar */
        .brand-header {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 12px 20px;
            background-color: #1b6338;
            border-radius: 10px;
            margin-bottom: 25px;
        }

        .brand-title {
            font-size: 1.4rem !important;
            font-weight: 800 !important;
            color: #ffffff !important;
            margin: 0 !important;
        }

        /* Τα μεγάλα Boxes */
        div[data-testid="stColumn"] {
            background-color: #6c8ebf !important;
            border-radius: 14px;
            padding: 16px 18px !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }

        /* 1. Επικεφαλίδες στα boxes */
        div[data-testid="stColumn"] h3, 
        div[data-testid="stColumn"] h4 {
            font-size: 1.15rem !important;
            font-weight: 700 !important;
            color: #000000 !important;
            margin-top: 0px !important;
            margin-bottom: 2px !important;
            padding-bottom: 0px !important;
        }

        /* 2. Περιγραφή */
        div[data-testid="stColumn"] p {
            font-size: 0.88rem !important;
            color: #111111 !important;
            font-weight: 400 !important;
            margin-top: 0px !important;
            margin-bottom: 8px !important;
            line-height: 1.2 !important;
        }

        /* 3. Κουμπιά: Απόλυτο κεντράρισμα & σταθερό ύψος */
        div[data-testid="stColumn"] .stButton > button {
            border-radius: 8px !important;
            height: 42px !important;
            min-height: 42px !important;
            padding: 0px 10px !important;
            color: #ffffff !important;
            border: none !important;
            background-color: #36456b !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
            margin-bottom: 6px !important;
        }

        div[data-testid="stColumn"] .stButton > button p,
        div[data-testid="stColumn"] .stButton > button div {
            font-size: 0.92rem !important;
            font-weight: 500 !important;
            color: #ffffff !important;
            margin: 0 !important;
            padding: 0 !important;
            text-align: center !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        div[data-testid="stColumn"] .stButton > button:hover {
            background-color: #28334f !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- ΣΥΝΔΕΣΗ ΜΕ GOOGLE SHEETS ---
@st.cache_resource
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    return gspread.authorize(creds)

def get_worksheet(sheet_name):
    client = get_gspread_client()
    sh = client.open("ImatioAppDB")
    return sh.worksheet(sheet_name)

# --- ΦΟΡΤΩΣΗ ΔΕΔΟΜΕΝΩΝ ---
def load_all_data():
    try:
        ws_c = get_worksheet("Customers")
        st.session_state['df_customers'] = pd.DataFrame(ws_c.get_all_records())
    except:
        st.session_state['df_customers'] = pd.DataFrame()

    try:
        ws_i = get_worksheet("Items")
        st.session_state['df_items'] = pd.DataFrame(ws_i.get_all_records())
    except:
        st.session_state['df_items'] = pd.DataFrame()

    try:
        ws_tx = get_worksheet("TrXalia")
        st.session_state['df_tr_xalia'] = pd.DataFrame(ws_tx.get_all_records())
    except:
        st.session_state['df_tr_xalia'] = pd.DataFrame()

    try:
        ws_ti = get_worksheet("TrEidi")
        st.session_state['df_tr_items'] = pd.DataFrame(ws_ti.get_all_records())
    except:
        st.session_state['df_tr_items'] = pd.DataFrame()

if 'df_customers' not in st.session_state or st.session_state['df_customers'].empty:
    load_all_data()

# --- ROUTING & MENU ---
if 'active_subview' not in st.session_state:
    st.session_state['active_subview'] = 'menu'

# --- HEADER WITH LOGO ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

logo_b64 = get_base64_image("logo.png")

if logo_b64:
    header_html = f"""
        <div class="brand-header">
            <img src="data:image/png;base64,{logo_b64}" style="height: 42px; width: auto; object-fit: contain;">
            <span class="brand-title">IMATIO-ΣΤΕΓΝΟΚΑΘΑΡΙΣΤΗΡΙΑ</span>
        </div>
    """
else:
    header_html = """
        <div class="brand-header">
            <span style="font-size: 1.6rem;">🧺</span>
            <span class="brand-title">IMATIO-ΣΤΕΓΝΟΚΑΘΑΡΙΣΤΗΡΙΑ</span>
        </div>
    """

st.markdown(header_html, unsafe_allow_html=True)

if st.session_state['active_subview'] != 'menu':
    if st.button("⬅️ Επιστροφή στο Κεντρικό Μενού"):
        st.session_state['active_subview'] = 'menu'
        st.rerun()
    st.markdown("---")

# 1. ΑΡΧΙΚΗ ΚΑΡΤΕΛΑ ΜΕΝΟΥ
if st.session_state['active_subview'] == 'menu':
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("### 🚚 Τμήμα Χαλιών")
        st.markdown("<p>Παραλαβή & επεξεργασία στοιχείων χαλιών</p>", unsafe_allow_html=True)
        
        if st.button("🚚 ΠΑΡΑΛΑΒΗ ΧΑΛΙΩΝ", use_container_width=True):
            st.session_state['active_subview'] = 'fast_loading'
            st.rerun()
            
        if st.button("✏️ ΤΡΟΠΟΠΟΙΗΣΗ & ΠΑΡΑΔΟΣΗ ΧΑΛΙΩΝ", use_container_width=True):
            st.session_state['active_subview'] = 'edit_xalia'
            st.rerun()

    with col2:
        st.markdown("### 👕 Τμήμα Ρούχων & Ειδών")
        st.markdown("<p>Παραλαβή & διαχείριση ραφιών/τιμών</p>", unsafe_allow_html=True)
        
        if st.button("👕 ΠΑΡΑΛΑΒΗ ΕΙΔΩΝ", use_container_width=True):
            st.session_state['active_subview'] = 'item_loading'
            st.rerun()
            
        if st.button("✏️ ΤΡΟΠΟΠΟΙΗΣΗ & ΠΑΡΑΔΟΣΗ ΡΟΥΧΩΝ", use_container_width=True):
            st.session_state['active_subview'] = 'edit_items'
            st.rerun()

    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    col_c1, col_c2 = st.columns(2, gap="large")
    
    with col_c1:
        st.markdown("### 👤 Διαχείριση Πελατών")
        st.markdown("<p>Καταχώρηση νέων πελατών & τροποποίηση στοιχείων</p>", unsafe_allow_html=True)
        
        if st.button("➕ Διαχείριση Πελατών (Νέα Εγγραφή)", use_container_width=True):
            st.session_state['active_subview'] = 'manage_customers_new'
            st.rerun()
            
        if st.button("✏️ Διαχείριση Πελατών (Τροποποίηση)", use_container_width=True):
            st.session_state['active_subview'] = 'manage_customers_edit'
            st.rerun()
            
    with col_c2:
        st.markdown("### 📦 Διαχείριση Καταλόγου Ειδών & Χαλιών")
        st.markdown("<p>Δημιουργία νέων ειδών/χαλιών & τροποποίηση καταλόγου</p>", unsafe_allow_html=True)
        
        if st.button("➕ Διαχείριση Καταλόγου (Νέα Εγγραφή)", use_container_width=True):
            st.session_state['active_subview'] = 'manage_catalog_new'
            st.rerun()
            
        if st.button("✏️ Διαχείριση Καταλόγου (Τροποποίηση)", use_container_width=True):
            st.session_state['active_subview'] = 'manage_catalog_edit'
            st.rerun()

# 2. ΠΑΡΑΛΑΒΗ ΧΑΛΙΩΝ
elif st.session_state['active_subview'] == 'fast_loading':
    admin_fast.render_fast_loading_tab(
        st.session_state['df_customers'],
        st.session_state['df_items'],
        get_worksheet
    )

# 3. ΤΡΟΠΟΠΟΙΗΣΗ ΧΑΛΙΩΝ
elif st.session_state['active_subview'] == 'edit_xalia':
    admin_eidi.render_edit_xalia_tab(
        st.session_state['df_tr_xalia'],
        st.session_state['df_customers'],
        get_worksheet
    )

# 4. ΠΑΡΑΛΑΒΗ ΕΙΔΩΝ
elif st.session_state['active_subview'] == 'item_loading':
    admin_eidi.render_item_loading_tab(
        st.session_state['df_customers'],
        st.session_state['df_items'],
        get_worksheet
    )

# 5. ΤΡΟΠΟΠΟΙΗΣΗ ΡΟΥΧΩΝ
elif st.session_state['active_subview'] == 'edit_items':
    admin_eidi.render_edit_items_tab(
        st.session_state['df_tr_items'],
        st.session_state['df_customers'],
        get_worksheet
    )

# 6. ΔΙΑΧΕΙΡΙΣΗ ΠΕΛΑΤΩΝ / ΚΑΤΑΛΟΓΟΥ
elif st.session_state['active_subview'] in ['manage_customers_new', 'manage_customers_edit', 'manage_catalog_new', 'manage_catalog_edit']:
    st.markdown("### ⚙️ Διαχείριση Ενότητας")
    st.info("Η φόρμα είναι έτοιμη για προσθήκη της αντίστοιχης λειτουργίας.")
