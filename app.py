import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import base64

import admin_fast
import admin_eidi

st.set_page_config(page_title="IMATIO", layout="wide", initial_sidebar_state="collapsed")

# --- STRICT CUSTOM STYLING ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 3.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 1200px;
        }

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

        div[data-testid="stColumn"] {
            background-color: #6c8ebf !important;
            border-radius: 14px;
            padding: 16px 18px !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }

        div[data-testid="stColumn"] h3, 
        div[data-testid="stColumn"] h4 {
            font-size: 1.15rem !important;
            font-weight: 700 !important;
            color: #000000 !important;
            margin-top: 0px !important;
            margin-bottom: 2px !important;
            padding-bottom: 0px !important;
        }

        div[data-testid="stColumn"] p {
            font-size: 0.88rem !important;
            color: #111111 !important;
            font-weight: 400 !important;
            margin-top: 0px !important;
            margin-bottom: 8px !important;
            line-height: 1.2 !important;
        }

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

# --- GOOGLE SHEETS CONNECTION ---
@st.cache_resource
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    return gspread.authorize(creds)

def get_worksheet(sheet_name):
    client = get_gspread_client()
    # Χρήση του ID του Google Sheet
    SPREADSHEET_ID = "18_Rke4EW04J0QaTw2PBgU1Q-NLgT7G2l3yR0NvX1jmE"
    sh = client.open_by_key(SPREADSHEET_ID)
    return sh.worksheet(sheet_name)

# --- ROBUST DATA LOADING ---
def load_all_data():
    try:
        ws_c = get_worksheet("Customers")
        data_c = ws_c.get_all_records()
        st.session_state['df_customers'] = pd.DataFrame(data_c) if data_c else pd.DataFrame(columns=["CustomerID", "CuName", "CuPhone", "CuAddress"])
    except Exception as e:
        st.session_state['df_customers'] = pd.DataFrame(columns=["CustomerID", "CuName", "CuPhone", "CuAddress"])
        st.error(f"Σφάλμα φόρτωσης Customers: {e}")

    try:
        ws_i = get_worksheet("Items")
        data_i = ws_i.get_all_records()
        st.session_state['df_items'] = pd.DataFrame(data_i) if data_i else pd.DataFrame()
    except:
        st.session_state['df_items'] = pd.DataFrame()

    try:
        ws_tx = get_worksheet("TrXalia")
        data_tx = ws_tx.get_all_records()
        st.session_state['df_tr_xalia'] = pd.DataFrame(data_tx) if data_tx else pd.DataFrame()
    except:
        st.session_state['df_tr_xalia'] = pd.DataFrame()

    try:
        ws_ti = get_worksheet("TrItems")
        data_ti = ws_ti.get_all_records()
        st.session_state['df_tr_items'] = pd.DataFrame(data_ti) if data_ti else pd.DataFrame()
    except:
        st.session_state['df_tr_items'] = pd.DataFrame()

if 'df_customers' not in st.session_state or st.session_state['df_customers'].empty:
    load_all_data()

# --- ROUTING & MENU ---
if 'active_subview' not in st.session_state:
    st.session_state['active_subview'] = 'menu'

# --- ROUTING & MENU MAP FOR HEADER TITLE ---
subview_titles = {
    'fast_loading': 'ΠΑΡΑΛΑΒΗ ΧΑΛΙΩΝ',
    'edit_xalia': 'ΤΡΟΠΟΠΟΙΗΣΗ ΧΑΛΙΩΝ',
    'item_loading': 'ΠΑΡΑΛΑΒΗ ΕΙΔΩΝ',
    'edit_items': 'ΤΡΟΠΟΠΟΙΗΣΗ ΡΟΥΧΩΝ',
    'manage_customers_new': 'ΝΕΑ ΕΓΓΡΑΦΗ ΠΕΛΑΤΗ',
    'manage_customers_edit': 'ΤΡΟΠΟΠΟΙΗΣΗ ΠΕΛΑΤΗ',
    'manage_catalog_new': 'ΝΕΟ ΕΙΔΟΣ ΚΑΤΑΛΟΓΟΥ',
    'manage_catalog_edit': 'ΤΡΟΠΟΠΟΙΗΣΗ ΚΑΤΑΛΟΓΟΥ'
}

current_page_title = subview_titles.get(st.session_state.get('active_subview', 'menu'), '')

# --- HEADER WITH LOGO & DYNAMIC PAGE TITLE ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

logo_b64 = get_base64_image("logo.png")

# CSS update για ομοιόμορφη στοίχιση και ίδια γραμματοσειρά
st.markdown("""
    <style>
        .brand-header {
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            padding: 12px 20px !important;
            background-color: #1b6338 !important;
            border-radius: 10px !important;
            margin-bottom: 25px !important;
        }
        .brand-header-left {
            display: flex !important;
            align-items: center !important;
            gap: 15px !important;
        }
    </style>
""", unsafe_allow_html=True)

if logo_b64:
    header_html = f"""
        <div class="brand-header">
            <div class="brand-header-left">
                <img src="data:image/png;base64,{logo_b64}" style="height: 42px; width: auto; object-fit: contain;">
                <span class="brand-title">IMATIO-ΣΤΕΓΝΟΚΑΘΑΡΙΣΤΗΡΙΑ</span>
            </div>
            <div>
                <span class="brand-title">{current_page_title}</span>
            </div>
        </div>
    """
else:
    header_html = f"""
        <div class="brand-header">
            <div class="brand-header-left">
                <span style="font-size: 1.6rem;">🧺</span>
                <span class="brand-title">IMATIO-ΣΤΕΓΝΟΚΑΘΑΡΙΣΤΗΡΙΑ</span>
            </div>
            <div>
                <span class="brand-title">{current_page_title}</span>
            </div>
        </div>
    """

st.markdown(header_html, unsafe_allow_html=True)

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
        st.session_state.get('df_customers', pd.DataFrame()),
        st.session_state.get('df_items', pd.DataFrame()),
        get_worksheet
    )

# 3. ΤΡΟΠΟΠΟΙΗΣΗ ΧΑΛΙΩΝ
elif st.session_state['active_subview'] == 'edit_xalia':
    admin_eidi.render_edit_xalia_tab(
        st.session_state.get('df_tr_xalia', pd.DataFrame()),
        st.session_state.get('df_customers', pd.DataFrame()),
        st.session_state.get('df_items', pd.DataFrame()),  # <--- Προστέθηκε αυτό
        get_worksheet
    )
# 4. ΠΑΡΑΛΑΒΗ ΕΙΔΩΝ
elif st.session_state['active_subview'] == 'item_loading':
    admin_eidi.render_item_loading_tab(
        st.session_state.get('df_customers', pd.DataFrame()),
        st.session_state.get('df_items', pd.DataFrame()),
        get_worksheet
    )

# 5. ΤΡΟΠΟΠΟΙΗΣΗ ΡΟΥΧΩΝ
elif st.session_state['active_subview'] == 'edit_items':
    admin_eidi.render_edit_items_tab(
        st.session_state.get('df_tr_items', pd.DataFrame()),
        st.session_state.get('df_customers', pd.DataFrame()),
        get_worksheet
    )

# 6. ΝΕΑ ΕΓΓΡΑΦΗ ΠΕΛΑΤΗ
elif st.session_state['active_subview'] == 'manage_customers_new':
    st.markdown("### ➕ Νέα Εγγραφή Πελάτη")
    with st.form("new_customer_form"):
        c_name = st.text_input("Ονοματεπώνυμο Πελάτη (CuName)")
        c_phone = st.text_input("Τηλέφωνο (CuPhone)")
        c_mobile = st.text_input("Κινητό (CuMobile)")
        c_address = st.text_input("Διεύθυνση (CuAddress)")
        c_city = st.text_input("Πόλη (CuCity)")
        c_email = st.text_input("Email (CuEmail)")
        submit_cust = st.form_submit_button("Αποθήκευση Πελάτη", type="primary")
        
        if submit_cust:
            if c_name:
                try:
                    ws_c = get_worksheet("Customers")
                    next_id = len(st.session_state['df_customers']) + 1
                    row_data = [next_id, c_name, c_address, c_city, c_phone, c_mobile, c_email]
                    ws_c.append_row(row_data)
                    load_all_data()
                    st.success(f"Ο πελάτης '{c_name}' αποθηκεύτηκε επιτυχώς!")
                except Exception as ex:
                    st.error(f"Σφάλμα αποθήκευσης: {ex}")
            else:
                st.warning("Παρακαλώ συμπληρώστε τουλάχιστον το όνομα του πελάτη.")

# 7. ΛΟΙΠΕΣ ΦΟΡΜΕΣ
elif st.session_state['active_subview'] in ['manage_customers_edit', 'manage_catalog_new', 'manage_catalog_edit']:
    st.markdown("### ⚙️ Διαχείριση Ενότητας")
    st.info("Η συγκεκριμένη φόρμα είναι έτοιμη για υλοποίηση.")
