import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import base64

# Eisagogi ton modules
import admin_fast
import admin_eidi

st.set_page_config(page_title="IMATIO", layout="wide", initial_sidebar_state="collapsed")

# --- MODERN RESPONSIVE STYLING ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 2.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 1200px;
        }

        .brand-header {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 12px 20px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            margin-bottom: 25px;
            backdrop-filter: blur(10px);
        }

        .brand-title {
            font-size: 1.35rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px;
            margin: 0 !important;
            padding: 0 !important;
        }

        div[data-testid="stColumn"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 20px;
            transition: all 0.2s ease-in-out;
        }

        div[data-testid="stColumn"]:hover {
            border-color: rgba(255, 255, 255, 0.2);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        }

        .stButton > button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 0.6rem 1rem !important;
            transition: transform 0.1s ease !important;
        }

        .stButton > button:active {
            transform: scale(0.98);
        }
    </style>
""", unsafe_allow_html=True)

# --- SYNDESI ME GOOGLE SHEETS ---
@st.cache_resource
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    return gspread.authorize(creds)

def get_worksheet(sheet_name):
    client = get_gspread_client()
    sh = client.open("ImatioAppDB")
    return sh.worksheet(sheet_name)

# --- FORTOSI DEDOMENON ME DIAGRAPHI SFALMATOS "DEN VRETHIKE PELATIS" ---
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
            <img src="data:image/png;base64,{logo_b64}" style="height: 40px; width: auto; object-fit: contain;">
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

# Koumpi epistrofis an eimaste se ypo-selida
if st.session_state['active_subview'] != 'menu':
    if st.button("⬅️ Επιστροφή στο Κεντρικό Μενού"):
        st.session_state['active_subview'] = 'menu'
        st.rerun()
    st.markdown("---")

# 1. ARXIKI KARTELA MENU
if st.session_state['active_subview'] == 'menu':
    
    # 📌 1. TMIMA PELATON KAI EIDON/XALION
    st.markdown("### 👤 Τμήμα Πελατών & Ειδών/Χαλιών")
    st.caption("Νέες εγγραφές πελατών, δημιουργία καταλόγου ειδών & τροποποιήσεις")
    
    col_cust1, col_cust2 = st.columns(2, gap="medium")
    with col_cust1:
        if st.button("➕/✏️ Διαχείριση Πελατών (Νέα Εγγραφή & Τροποποίηση)", use_container_width=True):
            st.session_state['active_subview'] = 'manage_customers'
            st.rerun()
    with col_cust2:
        if st.button("📦/✏️ Διαχείριση Καταλόγου Ειδών & Χαλιών", use_container_width=True):
            st.session_state['active_subview'] = 'manage_catalog'
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 📌 2. TMIMATA PARALAVIS / PARADOSIS
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("#### 🚚 Τμήμα Χαλιών")
        st.caption("Παραλαβή, παράδοση & επεξεργασία στοιχείων χαλιών")
        st.markdown("---")
        
        if st.button("🚛 ΠΑΡΑΛΑΒΗ / ΠΑΡΑΔΟΣΗ ΧΑΛΙΩΝ", use_container_width=True, type="primary"):
            st.session_state['active_subview'] = 'fast_loading'
            st.rerun()
            
        st.write("")
        if st.button("✏️ ΤΡΟΠΟΠΟΙΗΣΗ ΕΓΓΡΑΦΩΝ ΧΑΛΙΩΝ", use_container_width=True):
            st.session_state['active_subview'] = 'edit_xalia'
            st.rerun()

    with col2:
        st.markdown("#### 👕 Τμήμα Ρούχων & Ειδών")
        st.caption("Παραλαβή, παράδοση & διαχείριση ραφιών/τιμών")
        st.markdown("---")
        
        if st.button("👕 ΠΑΡΑΛΑΒΗ / ΠΑΡΑΔΟΣΗ ΕΙΔΩΝ", use_container_width=True, type="primary"):
            st.session_state['active_subview'] = 'item_loading'
            st.rerun()
            
        st.write("")
        if st.button("✏️ ΤΡΟΠΟΠΟΙΗΣΗ ΡΟΥΧΩΝ", use_container_width=True):
            st.session_state['active_subview'] = 'edit_items'
            st.rerun()

# 2. PARALAVI / PARADOSI XALION
elif st.session_state['active_subview'] == 'fast_loading':
    admin_fast.render_fast_loading_tab(
        st.session_state['df_customers'],
        st.session_state['df_items'],
        get_worksheet
    )

# 3. TROPOPOIISI XALION
elif st.session_state['active_subview'] == 'edit_xalia':
    admin_eidi.render_edit_xalia_tab(
        st.session_state['df_tr_xalia'],
        st.session_state['df_customers'],
        get_worksheet
    )

# 4. PARALAVI / PARADOSI EIDON
elif st.session_state['active_subview'] == 'item_loading':
    admin_eidi.render_item_loading_tab(
        st.session_state['df_customers'],
        st.session_state['df_items'],
        get_worksheet
    )

# 5. TROPOPOIISI ROUXON
elif st.session_state['active_subview'] == 'edit_items':
    admin_eidi.render_edit_items_tab(
        st.session_state['df_tr_items'],
        st.session_state['df_customers'],
        get_worksheet
    )

# 6. DIACHEIRISI PELATON
elif st.session_state['active_subview'] == 'manage_customers':
    st.markdown("### 👤 Διαχείριση Πελατών")
    st.info("Εδώ μπορείτε να προσθέτετε νέους πελάτες ή να επεξεργάζεστε τα στοιχεία τους.")
    # Klisi tis sinartisis pelaton opou xreiazetai

# 7. DIACHEIRISI KATALOGOU
elif st.session_state['active_subview'] == 'manage_catalog':
    st.markdown("### 📦 Κατάλογος Ειδών & Χαλιών")
    st.info("Εδώ μπορείτε να διαχειρίζεστε τους τύπους χαλιών, ρούχων και τις αρχικές τιμές μονάδας.")
