import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import base64

# Εισαγωγή των modules
import admin_fast
import admin_eidi

st.set_page_config(page_title="IMATIO", layout="wide", initial_sidebar_state="expanded")

# --- ΣΩΣΤΟ CSS ΓΙΑ ΝΑ ΜΗΝ ΚΟΒΕΤΑΙ Η ΕΠΙΚΕΦΑΛΙΔΑ ---
st.markdown("""
    <style>
        /* Σωστό padding για να μην κρύβεται τίποτα από το top-header του Streamlit */
        .block-container {
            padding-top: 3.5rem !important;
            padding-bottom: 2rem !important;
        }
        /* Αφαίρεση περιττών περιθωρίων */
        .main-header-container {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 25px;
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
if 'df_customers' not in st.session_state or st.session_state['df_customers'].empty:
    try:
        ws_c = get_worksheet("Customers")
        st.session_state['df_customers'] = pd.DataFrame(ws_c.get_all_records())
    except:
        st.session_state['df_customers'] = pd.DataFrame()

if 'df_items' not in st.session_state or st.session_state['df_items'].empty:
    try:
        ws_i = get_worksheet("Items")
        st.session_state['df_items'] = pd.DataFrame(ws_i.get_all_records())
    except:
        st.session_state['df_items'] = pd.DataFrame()

if 'df_tr_xalia' not in st.session_state or st.session_state['df_tr_xalia'].empty:
    try:
        ws_tx = get_worksheet("TrXalia")
        st.session_state['df_tr_xalia'] = pd.DataFrame(ws_tx.get_all_records())
    except:
        st.session_state['df_tr_xalia'] = pd.DataFrame()

if 'df_tr_items' not in st.session_state or st.session_state['df_tr_items'].empty:
    try:
        ws_ti = get_worksheet("TrEidi")
        st.session_state['df_tr_items'] = pd.DataFrame(ws_ti.get_all_records())
    except:
        st.session_state['df_tr_items'] = pd.DataFrame()


# --- ROUTING & MENU ---
if 'active_subview' not in st.session_state:
    st.session_state['active_subview'] = 'menu'

# --- ΑΣΦΑΛΗΣ ΜΕΘΟΔΟΣ ΕΜΦΑΝΙΣΗΣ LOGO + ΚΕΙΜΕΝΟΥ ΧΩΡΙΣ ΝΑ ΚΟΒΕΤΑΙ ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

logo_b64 = get_base64_image("logo.png")

if logo_b64:
    header_html = f"""
        <div class="main-header-container">
            <img src="data:image/png;base64,{logo_b64}" style="height: 45px; width: auto; object-fit: contain;">
            <span style="font-size: 1.3rem; font-weight: 700; color: white; line-height: 1;">IMATIO-ΣΤΕΓΝΟΚΑΘΑΡΙΣΤΗΡΙΑ</span>
        </div>
    """
else:
    header_html = """
        <div class="main-header-container">
            <span style="font-size: 1.8rem;">🧺</span>
            <span style="font-size: 1.3rem; font-weight: 700; color: white; line-height: 1;">IMATIO-ΣΤΕΓΝΟΚΑΘΑΡΙΣΤΗΡΙΑ</span>
        </div>
    """

st.markdown(header_html, unsafe_allow_html=True)

# Κουμπί επιστροφής αν βρισκόμαστε σε υπο-σελίδα
if st.session_state['active_subview'] != 'menu':
    if st.button("⬅️ Επιστροφή στο Κεντρικό Μενού"):
        st.session_state['active_subview'] = 'menu'
        st.rerun()
    st.markdown("---")

# 1. ΚΕΝΤΡΙΚΟ ΜΕΝΟΥ
if st.session_state['active_subview'] == 'menu':
    st.markdown("### 🎛️ Επιλέξτε Ενέργεια")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("🚚 **Διαχείριση Χαλιών**")
        if st.button("🚛 ΓΡΗΓΟΡΗ ΦΟΡΤΩΣΗ (Χαλιά)", use_container_width=True, type="primary"):
            st.session_state['active_subview'] = 'fast_loading'
            st.rerun()
            
        if st.button("✏️ ΤΡΟΠΟΠΟΙΗΣΗ ΕΓΓΡΑΦΩΝ ΧΑΛΙΩΝ", use_container_width=True):
            st.session_state['active_subview'] = 'edit_xalia'
            st.rerun()

    with col2:
        st.info("👕 **Διαχείριση Ρούχων & Ειδών**")
        if st.button("👕 ΚΑΤΑΧΩΡΗΣΗ ΡΟΥΧΩΝ / ΕΙΔΩΝ", use_container_width=True, type="primary"):
            st.session_state['active_subview'] = 'item_loading'
            st.rerun()
            
        if st.button("✏️ ΤΡΟΠΟΠΟΙΗΣΗ ΡΟΥΧΩΝ (Ράφι, Τιμή, Status)", use_container_width=True):
            st.session_state['active_subview'] = 'edit_items'
            st.rerun()

# 2. ΓΡΗΓΟΡΗ ΦΟΡΤΩΣΗ ΧΑΛΙΩΝ
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

# 4. ΚΑΤΑΧΩΡΗΣΗ ΡΟΥΧΩΝ
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
