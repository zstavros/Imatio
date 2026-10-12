import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(
    page_title="ImatioApp", 
    page_icon="🧺", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Κρύβει τα περιττά στοιχεία του Streamlit
hide_streamlit_style = """
    <style>
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    .stAppFooter {display: none !important;}
    .block-container {
        padding-top: 1rem !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

STATUS_OPTIONS = [
    "Έτοιμος για παραλαβή",
    "Προς επεξεργασία",
    "Προς φύλαξη",
    "Παραδόθηκε"
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

# Φόρτωση Δεδομένων
try:
    df_customers = load_tab_data("Customers")
    ws_customers = get_worksheet("Customers")

    df_items = load_tab_data("Items")
    ws_items = get_worksheet("Items")

    df_tr_items = load_tab_data("TrItems")
    ws_tr_items = get_worksheet("TrItems")

    df_tr_xalia = load_tab_data("TrXalia")
    ws_tr_xalia = get_worksheet("TrXalia")
except Exception as e:
    st.error(f"Σφάλμα σύνδεσης με Google Sheets: {e}")
    st.stop()

# --- ΚΕΝΤΡΙΚΗ ΟΘΟΝΗ: ΕΠΙΛΟΓΗ ΡΟΛΟΥ ---
st.title("🧺 ImatioApp")
user_role = st.radio(
    "Επιλέξτε ρόλο:", 
    ["📱 Πελάτης", "🔒 Διαχειριστής"], 
    horizontal=True
)

st.divider()

# ==========================================
# 📱 1. ΠΡΟΒΟΛΗ ΠΕΛΑΤΗ (CUSTOMER MODE)
# ==========================================
if user_role == "📱 Πελάτης":
    st.subheader("🔍 Αναζήτηση Παραγγελίας")
    st.write("Εισάγετε τον αριθμό του κινητού σας για να δείτε τα ρούχα και τα χαλιά σας.")

    user_phone = st.text_input("📞 Αριθμός Κινητού Τηλεφώνου", placeholder="π.χ. 6912345678").strip()

    if st.button("🔎 Αναζήτηση", type="primary"):
        if not user_phone:
            st.warning("Παρακαλώ εισάγετε έναν αριθμό τηλεφώνου.")
        else:
            phone_col = 'Mobile' if 'Mobile' in df_customers.columns else 'Phone'
            df_customers[phone_col] = df_customers[phone_col].astype(str).str.strip()
            matched_customer = df_customers[df_customers[phone_col] == user_phone]

            if matched_customer.empty:
                st.error("❌ Δεν βρέθηκε πελάτης με αυτό το τηλέφωνο.")
            else:
                cust_id = matched_customer['CustomerID'].values[0]
                cust_name = matched_customer['Name'].values[0]

                st.success(f"Γεια σας, **{cust_name}**! 👋")

                # Εμφάνιση Ρούχων (TrItems)
                st.subheader("👕 Τα Ρούχα μου (TrItems)")
                if not df_tr_items.empty and 'CustomerID' in df_tr_items.columns:
                    user_clothes = df_tr_items[df_tr_items['CustomerID'] == cust_id]
                else:
                    user_clothes = pd.DataFrame()

                if user_clothes.empty:
                    st.info("Δεν υπάρχουν καταχωρημένα ρούχα.")
                else:
                    for _, row in user_clothes.iterrows():
                        status = row.get('Status', 'Προς επεξεργασία')
                        with st.expander(f"Ρούχο #{int(row.get('TransactionID', 0))} - Κατάσταση: {status}"):
                            st.write(f"🏷️ **Είδος:** {row.get('ItName', '-')}")
                            st.write(f"📍 **Θέση/Ράφι:** {row.get('Place', '-')}")
                            st.write(f"💶 **Κόστος:** {row.get('TotalPrice', 0)}€")
                            st.write(f"📅 **Ημερομηνία:** {row.get('DateIn', '-')}")

                # Εμφάνιση Χαλιών (TrXalia)
                st.subheader("ρ carpet Τα Χαλιά μου (TrXalia)")
                if not df_tr_xalia.empty and 'CustomerID' in df_tr_xalia.columns:
                    user_carpets = df_tr_xalia[df_tr_xalia['CustomerID'] == cust_id]
                else:
                    user_carpets = pd.DataFrame()

                if user_carpets.empty:
                    st.info("Δεν υπάρχουν καταχωρημένα χαλιά.")
                else:
                    for _, row in user_carpets.iterrows():
                        status = row.get('Status', 'Προς επεξεργασία')
                        with st.expander(f"Χαλί #{int(row.get('TransactionID', 0))} - Κατάσταση: {status}"):
                            st.write(f"🏷️ **Είδος:** {row.get('ItName', '-')}")
                            st.write(f"📍 **Θέση/Ράφι:** {row.get('Place', '-')}")
                            st.write(f"💶 **Κόστος:** {row.get('TotalPrice', 0)}€")
                            st.write(f"📅 **Ημερομηνία:** {row.get('DateIn', '-')}")


# ==========================================
# 🔒 2. ΠΡΟΒΟΛΗ ΔΙΑΧΕΙΡΙΣΤΗ (ADMIN MODE)
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
        if st.button("🚪 Αποσύνδεση"):
            st.session_state.admin_logged_in = False
            st.cache_data.clear()
            st.rerun()

        st.subheader("🛠️ Πίνακας Ελέγχου Διαχειριστή")

        # --- ΝΕΑ ΚΑΤΑΧΩΡΗΣΗ (ΡΟΥΧΑ Ή ΧΑΛΙΑ) ---
        with st.form("new_entry_form", clear_on_submit=True):
            st.write("### ➕ Νέα Καταχώρηση")

            category_type = st.selectbox("Κατηγορία", ["👕 Ρούχα (TrItems)", "ρ carpet Χαλιά (TrXalia)"])

            customer_list = ["-- Νέος Πελάτης --"]
            if not df_customers.empty and 'Name' in df_customers.columns:
                phone_col = 'Mobile' if 'Mobile' in df_customers.columns else 'Phone'
                customer_list += [f"{row['Name']} ({row[phone_col]})" for _, row in df_customers.iterrows() if pd.notnull(row['Name'])]

            selected_customer = st.selectbox("Επιλογή Πελάτη", customer_list)

            new_name, new_phone = "", ""
            if selected_customer == "-- Νέος Πελάτης --":
                new_name = st.text_input("Όνομα Νέου Πελάτη")
                new_phone = st.text_input("Τηλέφωνο Νέου Πελάτη")

            item_name = st.text_input("Όνομα Είδους / Περιγραφή (π.χ. Μπουφάν, Μεγάλο Χαλί)")
            place_val = st.text_input("Θέση / Ράφι (Place)")
            price = st.number_input("Συνολικό Κόστος (€)", min_value=0.0, step=0.50)
            initial_status = st.selectbox("Αρχική Κατάσταση", STATUS_OPTIONS, index=1)

            submit_entry = st.form_submit_button("Καταχώρηση")

            if submit_entry:
                if selected_customer == "-- Νέος Πελάτης --":
                    if not new_name or not new_phone:
                        st.error("Συμπληρώστε όνομα και τηλέφωνο.")
                        st.stop()
                    cust_id = 1 if df_customers.empty or 'CustomerID' not in df_customers.columns else int(df_customers['CustomerID'].max()) + 1
                    ws_customers.append_row([cust_id, new_name, "", "", "", str(new_phone).strip(), "", ""])
                else:
                    cust_name_display = selected_customer.split(" (")[0]
                    cust_id = int(df_customers[df_customers['Name'] == cust_name_display]['CustomerID'].values[0])

                today_str = datetime.now().strftime("%Y-%m-%d %H:%M")

                if "Ρούχα" in category_type:
                    trans_id = 1 if df_tr_items.empty or 'TransactionID' not in df_tr_items.columns else int(df_tr_items['TransactionID'].max()) + 1
                    ws_tr_items.append_row([trans_id, cust_id, item_name, place_val, today_str, "", price, initial_status])
                    st.success(f"✅ Καταχωρήθηκε στα Ρούχα (ID: #{trans_id})!")
                else:
                    trans_id = 1 if df_tr_xalia.empty or 'TransactionID' not in df_tr_xalia.columns else int(df_tr_xalia['TransactionID'].max()) + 1
                    ws_tr_xalia.append_row([trans_id, cust_id, item_name, place_val, today_str, "", price, initial_status])
                    st.success(f"✅ Καταχωρήθηκε στα Χαλιά (ID: #{trans_id})!")
                
                st.cache_data.clear()
                st.rerun()

        # --- ΔΙΑΧΕΙΡΙΣΗ ΕΝΕΡΓΩΝ (Ρ
