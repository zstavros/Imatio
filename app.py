import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from admin_eidi import render_new_transaction_tab, render_active_transactions_tab
from admin_egg import render_customers_tab, render_items_tab

st.set_page_config(
    page_title="ImatioApp", 
    page_icon="🧺", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    header {visibility: hidden !important; height: 0px !important;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {display: none !important;}
    footer {visibility: hidden !important;}
    
    .block-container { 
        padding-top: 0rem !important; 
        margin-top: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        padding-bottom: 0rem !important;
    }
    
    [data-baseweb="tab"] p {
        font-size: 1.15rem !important;
        font-weight: 600 !important;
    }
    [data-baseweb="tab"] {
        font-size: 1.15rem !important;
    }
    </style>
""", unsafe_allow_html=True)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource(ttl=300)
def get_gspread_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def load_tab_data(tab_name):
    client = get_gspread_client()
    sheet_url = st.secrets["spreadsheet_url"]
    sh = client.open_by_url(sheet_url)
    worksheet = sh.worksheet(tab_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

def get_worksheet(tab_name):
    client = get_gspread_client()
    sheet_url = st.secrets["spreadsheet_url"]
    sh = client.open_by_url(sheet_url)
    return sh.worksheet(tab_name)

is_admin_logged_in = st.session_state.get("admin_logged_in", False)

if not is_admin_logged_in:
    st.title("🧺 ImatioApp")
    user_role = st.radio("Επιλέξτε ρόλο:", ["📱 Πελάτης", "🔒 Διαχειριστής"], horizontal=True)
    st.divider()
else:
    user_role = "🔒 Διαχειριστής"

# ==========================================
# 📱 ΟΘΟΝΗ ΠΕΛΑΤΗ
# ==========================================
if user_role == "📱 Πελάτης":
    st.subheader("🔍 Αναζήτηση Παραγγελίας")
    st.write("Εισάγετε τον αριθμό του κινητού σας για να δείτε τα ρούχα και τα χαλιά σας.")

    user_phone = st.text_input("📞 Αριθμός Κινητού Τηλεφώνου", placeholder="π.χ. 6912345678").strip()

    if st.button("🔎 Αναζήτηση", type="primary"):
        if not user_phone:
            st.warning("Παρακαλώ εισάγετε έναν αριθμό τηλεφώνου.")
        else:
            df_customers = load_tab_data("Customers")
            df_tr_items = load_tab_data("TrItems")
            df_tr_xalia = load_tab_data("TrXalia")

            phone_col = 'CuMobile' if 'CuMobile' in df_customers.columns else ('CuPhone' if 'CuPhone' in df_customers.columns else df_customers.columns[-1])
            df_customers[phone_col] = df_customers[phone_col].astype(str).str.strip()
            matched_customer = df_customers[df_customers[phone_col] == user_phone]

            if matched_customer.empty:
                st.error("❌ Δεν βρέθηκε πελάτης με αυτό το τηλέφωνο.")
            else:
                cust_id = matched_customer['CustomerID'].values[0]
                cust_name = matched_customer.get('CuName', matched_customer.get('Name')).values[0]
                st.success(f"Γεια σας, **{cust_name}**! 👋")

                st.subheader("👕 Τα Ρούχα μου (TrItems)")
                user_clothes = df_tr_items[df_tr_items['CustomerID'] == cust_id] if not df_tr_items.empty and 'CustomerID' in df_tr_items.columns else pd.DataFrame()
                if user_clothes.empty:
                    st.info("Δεν υπάρχουν καταχωρημένα ρούχα.")
                else:
                    for _, row in user_clothes.iterrows():
                        with st.expander(f"Ρούχο #{int(row.get('TransactionID', 0))} - Κατάσταση: {row.get('Status', '-')}"):
                            st.write(f"🏷️ **Είδος:** {row.get('ItName', '-')}")
                            st.write(f"📍 **Θέση/Ράφι:** {row.get('Place', '-')}")
                            st.write(f"💶 **Κόστος:** {row.get('TotalPrice', 0)}€")

                st.subheader("🧺 Τα Χαλιά μου (TrXalia)")
                user_carpets = df_tr_xalia[df_tr_xalia['CustomerID'] == cust_id] if not df_tr_xalia.empty and 'CustomerID' in df_tr_xalia.columns else pd.DataFrame()
                if user_carpets.empty:
                    st.info("Δεν υπάρχουν καταχωρημένα χαλιά.")
                else:
                    for _, row in user_carpets.iterrows():
                        with st.expander(f"Χαλί #{int(row.get('TransactionID', 0))} - Κατάσταση: {row.get('Status', '-')}"):
                            st.write(f"🏷️ **Είδος:** {row.get('ItName', '-')}")
                            st.write(f"📍 **Θέση/Ράφι:** {row.get('Place', '-')}")
                            st.write(f"💶 **Κόστος:** {row.get('TotalPrice', 0)}€")

# ==========================================
# 🔒 ΟΘΟΝΗ ΔΙΑΧΕΙΡΙΣΤΗ (LOGIN & DASHBOARD)
# ==========================================
else:
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        st.subheader("🔒 Περιοχή Διαχειριστή")
        entered_pass = st.text_input("Εισάγετε Κωδικό Διαχειριστή", type="password")
        
        if st.button("🔑 Σύνδεση", type="primary"):
            if entered_pass == "#G1orgos#":
                st.session_state.admin_logged_in = True
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("❌ Λανθασμένος κωδικός πρόσβασης.")
    else:
        # Δημιουργία των 5 κεντρικών καρτελών στην κορυφή του διαχειριστή
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📝 Νέα", 
            "📋 Ανοιχτά", 
            "👥 Πελάτες", 
            "👕 Είδη", 
            "🧺 Χαλιά"
        ])

        df_customers = load_tab_data("Customers")
        df_items = load_tab_data("Items")
        df_tr_items = load_tab_data("TrItems")
        df_tr_xalia = load_tab_data("TrXalia")

        with tab1:
            render_new_transaction_tab(df_customers, df_items, df_tr_items, df_tr_xalia, get_worksheet)

        with tab2:
            render_active_transactions_tab(df_tr_items, df_tr_xalia, df_customers, get_worksheet)

        with tab3:
            render_customers_tab(df_customers, get_worksheet)

        with tab4:
            render_items_tab(df_items, get_worksheet)

        with tab5:
            st.info("ℹ️ Χρησιμοποιείται η κεντρική βάση ειδών (Items) για καταχώρηση χαλιών.")
