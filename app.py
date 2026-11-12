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

# --- ULTRA STRICT CSS & BADGE BLOCKER ---
st.markdown("""
    <style>
        header {visibility: hidden !important; display: none !important;}
        #MainMenu {visibility: hidden !important; display: none !important;}
        footer {visibility: hidden !important; display: none !important;}
        
        .badge-blocker {
            position: fixed !important;
            bottom: 0 !important;
            right: 0 !important;
            width: 140px !important;
            height: 60px !important;
            background-color: #0e1117 !important;
            z-index: 999999999 !important;
            pointer-events: none !important;
        }

        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            max-width: 1200px;
        }

        .brand-header {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 10px 18px;
            background-color: #1b6338;
            border-radius: 10px;
            margin-bottom: 15px;
        }

        .brand-title {
            font-size: 1.3rem !important;
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

        div[data-testid="stDataFrame"] th {
            text-align: center !important;
            justify-content: center !important;
        }
        div[data-testid="stDataFrame"] td {
            text-align: center !important;
        }
        div[data-testid="stDataFrame"] td div {
            text-align: center !important;
            justify-content: center !important;
        }
    </style>
    <div class="badge-blocker"></div>
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

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

logo_b64 = get_base64_image("logo.png")

# ==========================================
# ΑΡΧΙΚΗ ΟΘΟΝΗ: ΠΕΛΑΤΗΣ & ADMIN PASSWORD LOGIN
# ==========================================
if not st.session_state['admin_logged_in']:
    if logo_b64:
        st.markdown(f"""
            <div class="brand-header" style="justify-content: center;">
                <img src="data:image/png;base64,{logo_b64}" style="height: 45px; width: auto; object-fit: contain;">
                <span class="brand-title" style="font-size: 1.5rem !important;">IMATIO - ΣΤΕΓΝΟΚΑΘΑΡΙΣΤΗΡΙΑ</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="brand-header" style="justify-content: center;">
                <span style="font-size: 1.6rem;">🧺</span>
                <span class="brand-title" style="font-size: 1.5rem !important;">IMATIO - ΣΤΕΓΝΟΚΑΘΑΡΙΣΤΗΡΙΑ</span>
            </div>
        """, unsafe_allow_html=True)

    col_empty, col_admin_btn = st.columns([5, 1])
    with col_admin_btn:
        if st.button("🔐 Διαχείριση", use_container_width=True):
            st.session_state['show_admin_modal'] = True

    if st.session_state.get('show_admin_modal', False):
        st.info("🔵 Σύνδεση Διαχειριστή")
        
        with st.form("admin_login_form"):
            pwd_input = st.text_input("Κωδικός Πρόσβασης Διαχειριστή:", type="password")
            submitted = st.form_submit_button("Σύνδεση")
            
            if submitted:
                correct_pwd = str(st.secrets.get("admin_password", "imatio123"))
                if pwd_input == correct_pwd:
                    st.session_state['admin_logged_in'] = True
                    st.session_state['show_admin_modal'] = False
                    st.rerun()
                else:
                    st.error("❌ Λάθος κωδικός πρόσβασης.")
                    
        if st.button("Ακύρωση", use_container_width=True, key="admin_modal_close"):
            st.session_state['show_admin_modal'] = False
            st.rerun()
            
        st.markdown("---")

    # ΚΥΡΙΟ VIEW ΓΙΑ ΤΟΝ ΠΕΛΑΤΗ
    st.markdown("<h3 style='text-align: center; color: #fff; margin-top: 5px;'>📱 Έτοιμα προς παράδοση</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #ccc; margin-bottom: 10px;'>Πληκτρολογήστε τον αριθμό του κινητού σας τηλεφώνου για να δείτε τα έτοιμα είδη σας.</p>", unsafe_allow_html=True)
    
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
                    'Είδος': r.get('ItName', '-'),
                    'Ημ. Παραλαβής': r.get('DateIn', '-'),
                    'Αξία €': f"{parse_price(r.get('TotalPrice', 0.0)):.2f}"
                })

        if not ready_items.empty:
            ri_matched = ready_items[ready_items.apply(check_match, axis=1)]
            for _, r in ri_matched.iterrows():
                results.append({
                    'Είδος': r.get('ItName', '-'),
                    'Ημ. Παραλαβής': r.get('DateIn', '-'),
                    'Αξία €': f"{parse_price(r.get('TotalPrice', 0.0)):.2f}"
                })

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        if results:
            st.success(f"🎉 Βρέθηκαν **{len(results)}** έτοιμα είδη για εσάς!")
            df_res = pd.DataFrame(results)
            st.dataframe(df_res, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Δεν βρέθηκαν έτοιμα είδη για αυτόν τον αριθμό τηλεφώνου.")

    st.stop()


# ==========================================
# ΠΕΡΙΒΑΛΛΟΝ ΔΙΑΧΕΙΡΙΣΤΗ (Admin Panel με TABS ψηλά)
# ==========================================
if logo_b64:
    header_html = f"""
        <div class="brand-header" style="justify-content: flex-start;">
            <img src="data:image/png;base64,{logo_b64}" style="height: 42px; width: auto; object-fit: contain;">
            <span class="brand-title">IMATIO - ΠΙΝΑΚΑΣ ΔΙΑΧΕΙΡΙΣΗΣ (ADMIN)</span>
        </div>
    """
else:
    header_html = f"""
        <div class="brand-header" style="justify-content: flex-start;">
            <span style="font-size: 1.6rem;">🧺</span>
            <span class="brand-title">IMATIO - ΠΙΝΑΚΑΣ ΔΙΑΧΕΙΡΙΣΗΣ (ADMIN)</span>
        </div>
    """

st.markdown(header_html, unsafe_allow_html=True)

# Δημιουργία Tabs στην κορυφή
tab_fast, tab_edit_x, tab_del_x, tab_item, tab_edit_i, tab_del_i, tab_cust_n, tab_cust_e, tab_cat_n, tab_cat_e, tab_analytics, tab_ready = st.tabs([
    "🚚 Παρ. Χαλιών", 
    "✏️ Τροπ. Χαλιών", 
    "✅ Παρδ. Χαλιά", 
    "👕 Παρ. Ρούχων", 
    "✏️ Τροπ. Ρούχων", 
    "✅ Παρδ. Ρούχα", 
    "➕ Νέος Πελ.", 
    "✏️ Τροπ. Πελ.", 
    "➕ Νέα Είδη", 
    "✏️ Τροπ. Ειδών", 
    "📊 Αναφορές & Top", 
    "📦 Έτοιμα"
])

with tab_fast:
    admin_fast.render_fast_loading_tab(
        st.session_state.get('df_customers', pd.DataFrame()),
        st.session_state.get('df_items', pd.DataFrame()),
        get_worksheet
    )

with tab_edit_x:
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

with tab_del_x:
    ws_tx = get_worksheet("TrXalia")
    data_tx = ws_tx.get_all_records()
    df_fresh_tx = pd.DataFrame(data_tx) if data_tx else pd.DataFrame()
    st.session_state['df_tr_xalia'] = df_fresh_tx
    
    admin_eidi.render_delivered_xalia_tab(
        df_fresh_tx,
        st.session_state.get('df_customers', pd.DataFrame()),
        get_worksheet
    )

with tab_item:
    admin_eidi.render_item_loading_tab(
        st.session_state.get('df_customers', pd.DataFrame()),
        st.session_state.get('df_items', pd.DataFrame()),
        get_worksheet
    )

with tab_edit_i:
    admin_eidi.render_edit_items_tab(
        st.session_state.get('df_tr_items', pd.DataFrame()),
        st.session_state.get('df_customers', pd.DataFrame()),
        get_worksheet
    )

with tab_del_i:
    ws_ti = get_worksheet("TrItems")
    data_ti = ws_ti.get_all_records()
    df_fresh_ti = pd.DataFrame(data_ti) if data_ti else pd.DataFrame()
    st.session_state['df_tr_items'] = df_fresh_ti
    
    admin_eidi.render_delivered_items_tab(
        df_fresh_ti,
        st.session_state.get('df_customers', pd.DataFrame()),
        get_worksheet
    )

with tab_cust_n:
    admin_egg.render_new_customer_tab(
        st.session_state.get('df_customers', pd.DataFrame()), 
        get_worksheet
    )

with tab_cust_e:
    ws_cust = get_worksheet("Customers")
    fresh_cust_data = ws_cust.get_all_records()
    df_fresh_customers = pd.DataFrame(fresh_cust_data) if fresh_cust_data else pd.DataFrame()
    st.session_state['df_customers'] = df_fresh_customers
    
    admin_egg.render_edit_customer_tab(
        df_fresh_customers, 
        get_worksheet
    )

with tab_cat_n:
    admin_egg.render_new_item_tab(
        st.session_state.get('df_items', pd.DataFrame()), 
        get_worksheet
    )

with tab_cat_e:
    ws_items = get_worksheet("Items")
    fresh_items_data = ws_items.get_all_records()
    df_fresh_items = pd.DataFrame(fresh_items_data) if fresh_items_data else pd.DataFrame()
    st.session_state['df_items'] = df_fresh_items
    
    admin_egg.render_edit_item_tab(
        df_fresh_items, 
        get_worksheet
    )

with tab_analytics:
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
            return pd.DataFrame(), 0.0
        df_f = df.copy()
        
        if 'Status' in df_f.columns:
            df_f = df_f[df_f['Status'].astype(str).str.strip() == "Παραδόθηκε"]
        else:
            return pd.DataFrame(), 0.0

        if 'DateOut' in df_f.columns:
            df_f['DateOut_dt'] = pd.to_datetime(df_f['DateOut'], errors='coerce', dayfirst=True)
            df_f = df_f[(df_f['DateOut_dt'] >= t_from) & (df_f['DateOut_dt'] <= t_to)]
        else:
            return pd.DataFrame(), 0.0

        if df_f.empty:
            return pd.DataFrame(), 0.0

        df_f['Price'] = df_f['TotalPrice'].apply(parse_price) if 'TotalPrice' in df_f.columns else 0.0
        total_rev = df_f['Price'].sum()
        return df_f, float(total_rev)

    df_x_filtered, rev_x = process_df_revenue(df_xalia)
    df_i_filtered, rev_i = process_df_revenue(df_items)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Έσοδα από Χαλιά", f"{rev_x:,.2f} €")
    m2.metric("Έσοδα από Ρούχα", f"{rev_i:,.2f} €")
    m3.metric("Συνολικός Τζίρος", f"{(rev_x + rev_i):,.2f} €")

    st.markdown("---")
    st.subheader("🏆 Top 10 Πελατών (με βάση τον τζίρο)")
    
    frames_to_concat = []
    if not df_x_filtered.empty:
        frames_to_concat.append(df_x_filtered)
    if not df_i_filtered.empty:
        frames_to_concat.append(df_i_filtered)
        
    if frames_to_concat:
        all_delivered = pd.concat(frames_to_concat, ignore_index=True)
        
        if 'CustomerName' in all_delivered.columns and not all_delivered.empty:
            top_cust = all_delivered.groupby('CustomerName')['Price'].sum().reset_index()
            top_cust = top_cust.sort_values(by='Price', ascending=False).head(10)
            top_cust.columns = ['Πελάτης', 'Συνολικός Τζίρος (€)']
            top_cust['Συνολικός Τζίρος (€)'] = top_cust['Συνολικός Τζίρος (€)'].apply(lambda x: f"{x:,.2f} €")
            st.dataframe(top_cust, use_container_width=True, hide_index=True)
        else:
            st.info("Δεν βρέθηκαν δεδομένα πελατών για την επιλεγμένη περίοδο.")
            
        st.markdown("---")
        st.subheader("🔥 Top 10 Δημοφιλή Είδη")
        if 'ItName' in all_delivered.columns and not all_delivered.empty:
            top_items = all_delivered.groupby('ItName').size().reset_index(name='Ποσότητα')
            top_items = top_items.sort_values(by='Ποσότητα', ascending=False).head(10)
            top_items.columns = ['Είδος', 'Πλήθος Παραγγελιών']
            st.dataframe(top_items, use_container_width=True, hide_index=True)
        else:
            st.info("Δεν βρέθηκαν δεδομένα ειδών για την επιλεγμένη περίοδο.")
    else:
        st.info("Δεν υπάρχουν παραδόσεις για την επιλεγμένη χρονική περίοδο ώστε να εμφανιστούν τα Top 10.")

with tab_ready:
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
