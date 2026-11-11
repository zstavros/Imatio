import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import base64
from datetime import datetime, date

import admin_fast
import admin_eidi
import admin_egg

st.set_page_config(page_title="IMATIO", layout="wide", initial_sidebar_state="collapsed")

# --- STRICT CUSTOM STYLING ---
st.markdown("""
    <style>
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        .viewerBadge_link__1S137 {display: none !important;}
        div[class*="viewerBadge"] {display: none !important;}
        
        .block-container {
            padding-top: 1.5rem !important;
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

        .stButton > button,
        div[data-testid="stFormSubmitButton"] > button {
            background-color: #36456b !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: 500 !important;
            height: 42px !important;
            min-height: 42px !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
            box-shadow: none !important;
        }

        .stButton > button p,
        .stButton > button div,
        div[data-testid="stFormSubmitButton"] > button p,
        div[data-testid="stFormSubmitButton"] > button div {
            font-size: 0.92rem !important;
            font-weight: 500 !important;
            color: #ffffff !important;
            margin: 0 !important;
            padding: 0 !important;
            text-align: center !important;
        }

        .stButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #28334f !important;
        }

        div[data-testid="stForm"] {
            border: none !important;
            padding: 0px !important;
            background-color: transparent !important;
        }

        .menu-cards div[data-testid="stColumn"] {
            background-color: #6c8ebf !important;
            border-radius: 14px;
            padding: 16px 18px !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
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
    SPREADSHEET_ID = "18_Rke4EW04J0QaTw2PBgU1Q-NLgT7G2l3yR0NvX1jmE"
    sh = client.open_by_key(SPREADSHEET_ID)
    return sh.worksheet(sheet_name)

# --- PRICE PARSER ---
def parse_price(val):
    if pd.isna(val) or val == "" or val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s_val = str(val).strip().replace('€', '').replace(' ', '')
    if not s_val:
        return 0.0
    s_val = s_val.replace('.', '').replace(',', '.') if ',' in s_val and '.' in s_val else s_val.replace(',', '.')
    try:
        return float(s_val)
    except:
        return 0.0

# --- FAST DATA LOADING ---
def load_all_data():
    try:
        ws_c = get_worksheet("Customers")
        data_c = ws_c.get_all_records()
        st.session_state['df_customers'] = pd.DataFrame(data_c) if data_c else pd.DataFrame(columns=["CustomerID", "CuName", "CuPhone", "CuAddress"])
    except:
        st.session_state['df_customers'] = pd.DataFrame(columns=["CustomerID", "CuName", "CuPhone", "CuAddress"])

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

if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False

if 'active_subview' not in st.session_state:
    st.session_state['active_subview'] = 'menu'

subview_titles = {
    'fast_loading': 'ΠΑΡΑΛΑΒΗ ΧΑΛΙΩΝ',
    'edit_xalia': 'ΤΡΟΠΟΠΟΙΗΣΗ ΠΑΡ.ΧΑΛΙΩΝ',
    'delivered_xalia': 'ΠΑΡΑΔΟΜΕΝΑ ΧΑΛΙΑ',
    'item_loading': 'ΠΑΡΑΛΑΒΗ ΡΟΥΧΩΝ',
    'edit_items': 'ΤΡΟΠΟΠΟΙΗΣΗ ΠΑΡ.ΡΟΥΧΩΝ',
    'delivered_items': 'ΠΑΡΑΔΟΜΕΝΑ ΡΟΥΧΑ',
    'manage_customers_new': 'ΝΕΟΣ ΠΕΛΑΤΗΣ',
    'manage_customers_edit': 'ΤΡΟΠΟΠΟΙΗΣΗ ΠΕΛΑΤΗ',
    'manage_catalog_new': 'ΝΕΑ ΕΙΔΗ & ΧΑΛΙΑ',
    'manage_catalog_edit': 'ΤΡΟΠΟΠΟΙΗΣΗ ΕΙΔΩΝ-ΧΑΛΙΩΝ',
    'analytics': 'ΑΝΑΦΟΡΕΣ & ΣΤΑΤΙΣΤΙΚΑ',
    'ready_orders': 'ΕΤΟΙΜΑ ΠΡΟΣ ΠΑΡΑΔΟΣΗ'
}

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

logo_b64 = get_base64_image("logo.png")

# ==========================================
# ΑΡΧΙΚΗ ΟΘΟΝΗ: ΠΕΛΑΤΗΣ & ADMIN LOGIN
# ==========================================
if not st.session_state['admin_logged_in']:
    if logo_b64:
        st.markdown(f"""
            <div class="brand-header" style="justify-content: center;">
                <img src="data:image/png;base64,{logo_b64}" style="height: 50px; width: auto; object-fit: contain;">
                <span class="brand-title" style="font-size: 1.6rem !important;">IMATIO - ΣΤΕΓΝΟΚΑΘΑΡΙΣΤΗΡΙΑ</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="brand-header" style="justify-content: center;">
                <span style="font-size: 1.8rem;">🧺</span>
                <span class="brand-title" style="font-size: 1.6rem !important;">IMATIO - ΣΤΕΓΝΟΚΑΘΑΡΙΣΤΗΡΙΑ</span>
            </div>
        """, unsafe_allow_html=True)

    # Top bar με κουμπί διαχειριστή στη γωνία
    col_empty, col_admin_btn = st.columns([5, 1])
    with col_admin_btn:
        if st.button("🔐 Διαχείριση", use_container_width=True):
            st.session_state['show_admin_modal'] = True

    # Εάν πατηθεί η διαχείριση, ελέγχουμε τα επιτρεπόμενα emails από τα Secrets (1ος τρόπος)
    if st.session_state.get('show_admin_modal', False):
        st.info("🔵 Σύνδεση Διαχειριστή")
        user_email_input = st.text_input("Εισάγετε το Email Διαχειριστή (Gmail/Yahoo):", key="admin_email_box")
        
        # Ανάκτηση των 2 emails από τα secrets
        email_1 = str(st.secrets.get("admin_email", "")).strip().lower()
        email_2 = str(st.secrets.get("admin_email_2", "")).strip().lower()
        allowed_admins = [e for e in [email_1, email_2] if e]

        col_ok, col_cancel = st.columns(2)
        with col_ok:
            if st.button("Είσοδος", use_container_width=True, key="admin_email_submit"):
                clean_input = user_email_input.strip().lower()
                if clean_input in allowed_admins:
                    st.session_state['admin_logged_in'] = True
                    st.session_state['show_admin_modal'] = False
                    st.rerun()
                else:
                    st.error("⚠️ Το email αυτό δεν διαθέτει δικαιώματα διαχειριστή.")
        with col_cancel:
            if st.button("Ακύρωση", use_container_width=True, key="admin_email_cancel"):
                st.session_state['show_admin_modal'] = False
                st.rerun()
        st.markdown("---")

    # ΚΥΡΙΟ VIEW ΓΙΑ ΤΟΝ ΠΕΛΑΤΗ (Ανοιχτό πλαίσιο τηλεφώνου)
    st.markdown("<br><h3 style='text-align: center; color: #fff;'>📱 Έτοιμα προς παράδοση</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #ccc;'>Πληκτρολογήστε τον αριθμό του κινητού σας τηλεφώνου για να δείτε τα έτοιμα είδη σας.</p>", unsafe_allow_html=True)
    
    col_c1, col_search, col_c2 = st.columns([1, 2, 1])
    with col_search:
        phone_input = st.text_input("📞 Αριθμός Κινητού Τηλεφώνου:", placeholder="")

    if phone_input:
        clean_search_phone = phone_input.replace(" ", "").replace("-", "").strip()
        df_cust = st.session_state.get('df_customers', pd.DataFrame())
        
        matched_customer_names = []
        if not df_cust.empty:
            df_cust.columns = df_cust.columns.str.strip()
            phone_cols = [c for c in ['CuMobile', 'CuPhone', 'Mobile', 'Phone', 'TEL', 'Τηλέφωνο'] if c in df_cust.columns]
            
            for _, row in df_cust.iterrows():
                for p_col in phone_cols:
                    val_p = str(row.get(p_col, ''))
                    clean_db_p = val_p.replace(" ", "").replace("-", "").replace("+", "").replace("(", "").replace(")", "").strip()
                    
                    if clean_search_phone != "" and (clean_search_phone == clean_db_p or clean_db_p.endswith(clean_search_phone)):
                        c_n = str(row.get('CuName', row.get('Name', ''))).strip()
                        if c_n and c_n not in matched_customer_names:
                            matched_customer_names.append(c_n)

        df_xalia = st.session_state.get('df_tr_xalia', pd.DataFrame())
        df_items = st.session_state.get('df_tr_items', pd.DataFrame())

        ready_xalia = pd.DataFrame()
        ready_items = pd.DataFrame()

        if not df_xalia.empty and 'Status' in df_xalia.columns:
            ready_xalia = df_xalia[df_xalia['Status'].astype(str).str.strip().str.lower() == 'έτοιμο'].copy()
            
        if not df_items.empty and 'Status' in df_items.columns:
            ready_items = df_items[df_items['Status'].astype(str).str.strip().str.lower() == 'έτοιμο'].copy()

        results = []

        def check_match(row):
            c_name = str(row.get('CustomerName', '')).strip()
            return c_name in matched_customer_names

        if not ready_xalia.empty:
            rx_matched = ready_xalia[ready_xalia.apply(check_match, axis=1)]
            for _, r in rx_matched.iterrows():
                results.append({
                    'Κατηγορία': '🧶 Χαλί',
                    'Είδος (ItName)': r.get('ItName', '-'),
                    'Ημερομηνία Παραλαβής (DateIn)': r.get('DateIn', '-'),
                    'Συνολική Τιμή (TotalPrice)': parse_price(r.get('TotalPrice', 0.0))
                })

        if not ready_items.empty:
            ri_matched = ready_items[ready_items.apply(check_match, axis=1)]
            for _, r in ri_matched.iterrows():
                results.append({
                    'Κατηγορία': '👔 Ρούχο / Είδος',
                    'Είδος (ItName)': r.get('ItName', '-'),
                    'Ημερομηνία Παραλαβής (DateIn)': r.get('DateIn', '-'),
                    'Συνολική Τιμή (TotalPrice)': parse_price(r.get('TotalPrice', 0.0))
                })

        st.markdown("<br>", unsafe_allow_html=True)
        if results:
            st.success(f"🎉 Βρέθηκαν **{len(results)}** έτοιμα είδη για εσάς!")
            df_res = pd.DataFrame(results)
            st.dataframe(df_res, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Δεν βρέθηκαν έτοιμα είδη για αυτόν τον αριθμό τηλεφώνου.")

    st.stop()


# ==========================================
# ΠΕΡΙΒΑΛΛΟΝ ΔΙΑΧΕΙΡΙΣΤΗ (Admin Panel)
# ==========================================
current_subview = st.session_state.get('active_subview', 'menu')
if current_subview == 'menu':
    header_text = "IMATIO - ΠΙΝΑΚΑΣ ΔΙΑΧΕΙΡΙΣΗΣ (ADMIN)"
else:
    header_text = subview_titles.get(current_subview, "")

if logo_b64:
    header_html = f"""
        <div class="brand-header" style="justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 15px;">
                <img src="data:image/png;base64,{logo_b64}" style="height: 42px; width: auto; object-fit: contain;">
                <span class="brand-title">{header_text}</span>
            </div>
    """
else:
    header_html = f"""
        <div class="brand-header" style="justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 15px;">
                <span style="font-size: 1.6rem;">🧺</span>
                <span class="brand-title">{header_text}</span>
            </div>
    """

st.markdown(header_html + "</div>", unsafe_allow_html=True)

col_logout_space, col_logout_btn = st.columns([5, 1])
with col_logout_btn:
    if st.button("🔒 ΑΠΟΣΥΝΔΕΣΗ", use_container_width=True):
        st.session_state['admin_logged_in'] = False
        st.session_state['active_subview'] = 'menu'
        st.rerun()

# --- ΚΕΝΤΡΙΚΟ ΜΕΝΟΥ ΔΙΑΧΕΙΡΙΣΤΗ ---
if st.session_state['active_subview'] == 'menu':
    st.markdown('<div class="menu-cards">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("##### 🚚 Τμήμα Χαλιών")
        if st.button("🚚 ΠΑΡΑΛΑΒΗ ΧΑΛΙΩΝ", use_container_width=True):
            st.session_state['active_subview'] = 'fast_loading'
            st.rerun()
            
        if st.button("✏️ ΤΡΟΠΟΠΟΙΗΣΗ & ΠΑΡΑΔΟΣΗ ΧΑΛΙΩΝ", use_container_width=True):
            st.session_state['active_subview'] = 'edit_xalia'
            st.rerun()

        if st.button("✅ ΠΑΡΑΔΟΜΕΝΑ ΧΑΛΙΑ", use_container_width=True):
            st.session_state['active_subview'] = 'delivered_xalia'
            st.rerun()

    with col2:
        st.markdown("##### 👕 Τμήμα Ρούχων")
        if st.button("👕 ΠΑΡΑΛΑΒΗ ΡΟΥΧΩΝ", use_container_width=True):
            st.session_state['active_subview'] = 'item_loading'
            st.rerun()
            
        if st.button("✏️ ΤΡΟΠΟΠΟΙΗΣΗ & ΠΑΡΑΔΟΣΗ ΡΟΥΧΩΝ", use_container_width=True):
            st.session_state['active_subview'] = 'edit_items'
            st.rerun()

        if st.button("✅ ΠΑΡΑΔΟΜΕΝΑ ΡΟΥΧΑ", use_container_width=True):
            st.session_state['active_subview'] = 'delivered_items'
            st.rerun()

    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    col_c1, col_c2 = st.columns(2, gap="large")
    
    with col_c1:
        st.markdown("##### 👤 Διαχείριση Πελατών")
        if st.button("➕ ΝΕΟΣ ΠΕΛΑΤΗΣ", use_container_width=True):
            st.session_state['active_subview'] = 'manage_customers_new'
            st.rerun()
            
        if st.button("✏️ ΤΡΟΠΟΠΟΙΗΣΗ ΠΕΛΑΤΩΝ", use_container_width=True):
            st.session_state['active_subview'] = 'manage_customers_edit'
            st.rerun()
            
    with col_c2:
        st.markdown("##### 📦 Διαχείριση Ειδών & Χαλιών")
        if st.button("➕ ΝΕΑ ΕΙΔΗ & ΧΑΛΙΑ", use_container_width=True):
            st.session_state['active_subview'] = 'manage_catalog_new'
            st.rerun()
            
        if st.button("✏️ ΤΡΟΠΟΠΟΙΗΣΗ ΕΙΔΩΝ & ΧΑΛΙΩΝ", use_container_width=True):
            st.session_state['active_subview'] = 'manage_catalog_edit'
            st.rerun()

    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    col_an1, col_an2 = st.columns(2, gap="large")
    with col_an1:
        st.markdown("##### 📊 Αναφορές & Στατιστικά")
        if st.button("📈 ΠΡΟΒΟΛΗ ΑΝΑΦΟΡΩΝ & ΤΖΙΡΟΥ", use_container_width=True):
            st.session_state['date_from'] = date.today()
            st.session_state['date_to'] = date.today()
            st.session_state['active_subview'] = 'analytics'
            st.rerun()
            
    with col_an2:
        st.markdown("##### 📦 Έτοιμα προς Παράδοση")
        if st.button("📦 ΤΙ ΕΧΟΥΜΕ ΑΠΟ ΕΤΟΙΜΑ", use_container_width=True):
            st.session_state['active_subview'] = 'ready_orders'
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state['active_subview'] == 'fast_loading':
    admin_fast.render_fast_loading_tab(
        st.session_state.get('df_customers', pd.DataFrame()),
        st.session_state.get('df_items', pd.DataFrame()),
        get_worksheet
    )

elif st.session_state['active_subview'] == 'edit_xalia':
    ws_tx = get_worksheet("TrXalia")
    data_tx = ws_tx.get_all_records()
    df_fresh_tx = pd.DataFrame(data_tx) if data_tx else pd.DataFrame()
    st.session_state['df_tr_xalia'] = df_fresh_tx
    
    admin_eidi.render_edit_xalia_tab(
        df_fresh_tx,
        st.session_state.get('df_customers', pd.DataFrame()),
        st.session_state.get('df_items', pd.DataFrame()),
        get_worksheet
    )

elif st.session_state['active_subview'] == 'delivered_xalia':
    ws_tx = get_worksheet("TrXalia")
    data_tx = ws_tx.get_all_records()
    df_fresh_tx = pd.DataFrame(data_tx) if data_tx else pd.DataFrame()
    st.session_state['df_tr_xalia'] = df_fresh_tx
    
    admin_eidi.render_delivered_xalia_tab(
        df_fresh_tx,
        st.session_state.get('df_customers', pd.DataFrame()),
        get_worksheet
    )

elif st.session_state['active_subview'] == 'item_loading':
    admin_eidi.render_item_loading_tab(
        st.session_state.get('df_customers', pd.DataFrame()),
        st.session_state.get('df_items', pd.DataFrame()),
        get_worksheet
    )

elif st.session_state['active_subview'] == 'edit_items':
    admin_eidi.render_edit_items_tab(
        st.session_state.get('df_tr_items', pd.DataFrame()),
        st.session_state.get('df_customers', pd.DataFrame()),
        get_worksheet
    )

elif st.session_state['active_subview'] == 'delivered_items':
    ws_ti = get_worksheet("TrItems")
    data_ti = ws_ti.get_all_records()
    df_fresh_ti = pd.DataFrame(data_ti) if data_ti else pd.DataFrame()
    st.session_state['df_tr_items'] = df_fresh_ti
    
    admin_eidi.render_delivered_items_tab(
        df_fresh_ti,
        st.session_state.get('df_customers', pd.DataFrame()),
        get_worksheet
    )

elif st.session_state['active_subview'] == 'manage_customers_new':
    admin_egg.render_new_customer_tab(
        st.session_state.get('df_customers', pd.DataFrame()), 
        get_worksheet
    )

elif st.session_state['active_subview'] == 'manage_customers_edit':
    ws_cust = get_worksheet("Customers")
    fresh_cust_data = ws_cust.get_all_records()
    df_fresh_customers = pd.DataFrame(fresh_cust_data) if fresh_cust_data else pd.DataFrame()
    st.session_state['df_customers'] = df_fresh_customers
    
    admin_egg.render_edit_customer_tab(
        df_fresh_customers, 
        get_worksheet
    )

elif st.session_state['active_subview'] == 'manage_catalog_new':
    admin_egg.render_new_item_tab(
        st.session_state.get('df_items', pd.DataFrame()), 
        get_worksheet
    )

elif st.session_state['active_subview'] == 'manage_catalog_edit':
    ws_items = get_worksheet("Items")
    fresh_items_data = ws_items.get_all_records()
    df_fresh_items = pd.DataFrame(fresh_items_data) if fresh_items_data else pd.DataFrame()
    st.session_state['df_items'] = df_fresh_items
    
    admin_egg.render_edit_item_tab(
        df_fresh_items, 
        get_worksheet
    )

elif st.session_state['active_subview'] == 'analytics':
    col_btn, _ = st.columns([1, 4])
    with col_btn:
        if st.button("🏠 ΑΡΧΙΚΗ", use_container_width=True):
            st.session_state['active_subview'] = 'menu'
            st.rerun()
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
    
    df_xalia = st.session_state.get('df_tr_xalia', pd.DataFrame())
    df_items = st.session_state.get('df_tr_items', pd.DataFrame())
    
    today = date.today()
    if 'date_from' not in st.session_state:
        st.session_state['date_from'] = today
    if 'date_to' not in st.session_state:
        st.session_state['date_to'] = today

    st.subheader("📅 Επιλογή Χρονικού Διαστήματος")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📆 ΣΗΜΕΡΑ", use_container_width=True):
            st.session_state['date_from'] = today
            st.session_state['date_to'] = today
            st.rerun()
    with c2:
        if st.button("🗓️ ΤΡΕΧΩΝ ΜΗΝΑΣ", use_container_width=True):
            st.session_state['date_from'] = today.replace(day=1)
            st.session_state['date_to'] = today
            st.rerun()
    with c3:
        if st.button("📊 ΤΡΕΧΟΝ ΕΤΟΣ", use_container_width=True):
            st.session_state['date_from'] = today.replace(month=1, day=1)
            st.session_state['date_to'] = today
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        date_from = st.date_input("Από Ημερομηνία:", value=st.session_state['date_from'])
    with f_col2:
        date_to = st.date_input("Έως Ημερομηνία:", value=st.session_state['date_to'])

    t_from = pd.to_datetime(date_from)
    t_to = pd.to_datetime(date_to) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

    def process_df_revenue(df):
        if df.empty:
            return pd.DataFrame()
        df_f = df.copy()
        if 'DateOut' in df_f.columns:
            df_f['DateOut'] = pd.to_datetime(df_f['DateOut'], errors='coerce', dayfirst=True)
            df_f = df_f[(df_f['DateOut'] >= t_from) & (df_f['DateOut'] <= t_to)]
        if 'Status' in df_f.columns:
            df_f = df_f[df_f['Status'].astype(str).str.strip() == "Παραδόθηκε"]
        df_f['Price'] = df_f['TotalPrice'].apply(parse_price) if 'TotalPrice' in df_f.columns else 0.0
        return df_f

    rev_x = process_df_revenue(df_xalia)['Price'].sum()
    rev_i = process_df_revenue(df_items)['Price'].sum()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Έσοδα από Χαλιά", f"{rev_x:,.2f} €")
    m2.metric("Έσοδα από Ρούχα", f"{rev_i:,.2f} €")
    m3.metric("Συνολικός Τζίρος", f"{(rev_x + rev_i):,.2f} €")

elif st.session_state['active_subview'] == 'ready_orders':
    col_btn, _ = st.columns([1, 4])
    with col_btn:
        if st.button("🏠 ΑΡΧΙΚΗ", use_container_width=True):
            st.session_state['active_subview'] = 'menu'
            st.rerun()
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
    
    df_xalia = st.session_state.get('df_tr_xalia', pd.DataFrame())
    df_items = st.session_state.get('df_tr_items', pd.DataFrame())
    df_cust = st.session_state.get('df_customers', pd.DataFrame())

    def get_ready_df(df, type_label):
        if df.empty or 'Status' not in df.columns:
            return pd.DataFrame()
        df_f = df[df['Status'].astype(str).str.strip() == "Έτοιμο"].copy()
        df_f['Price'] = df_f['TotalPrice'].apply(parse_price) if 'TotalPrice' in df_f.columns else 0.0
        df_f['Τύπος'] = type_label
        return df_f

    combined_ready = pd.concat([get_ready_df(df_xalia, "Χαλί"), get_ready_df(df_items, "Ρούχο")], ignore_index=True)

    st.subheader("📋 Έτοιμα προς παράδοση")
    if not combined_ready.empty:
        report_data = []
        for _, row in combined_ready.iterrows():
            c_name = str(row.get('CustomerName', '')).strip()
            p_num = "Δεν καταχωρήθηκε"
            if not df_cust.empty and 'CuName' in df_cust.columns:
                match_c = df_cust[df_cust['CuName'].astype(str).str.strip() == c_name]
                if not match_c.empty and 'CuPhone' in match_c.columns:
                    val_phone = match_c['CuPhone'].values[0]
                    if pd.notna(val_phone) and str(val_phone).strip() != "":
                        p_num = str(val_phone).strip()

            report_data.append({
                'Πελάτης': c_name if c_name else 'Άγνωστος',
                'Τηλέφωνο': p_num,
                'Κατηγορία': row.get('Τύπος'),
                'Είδος': row.get('ItName', 'Είδος'),
                'Αξία (€)': row.get('Price', 0.0)
            })
        st.dataframe(pd.DataFrame(report_data), use_container_width=True, hide_index=True)
    else:
        st.info("🎉 Προς το παρόν δεν υπάρχουν παραγγελίες με κατάσταση 'Έτοιμο'.")
