import json
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(
    page_title="ImatioApp", 
    page_icon="🧺", 
    layout="centered",
    initial_sidebar_state="expanded"  # Κλείνει αυτόματα την πλευρική μπάρα
)

# Κρύβει τα κουμπιά GitHub, Fork, Streamlit menu & Footer
hide_streamlit_style = """
    <style>
    /* Κρύβει μόνο το μενού, τα εργαλεία και το footer, αφήνοντας το κουμπί της sidebar */
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    .stAppFooter {display: none !important;}
    
    /* Αφαιρεί το πάνω περιθώριο */
    .block-container {
        padding-top: 1.5rem !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Λίστα με τα 4 νέα Statuses
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

def load_tab(tab_name):
    client = get_gspread_client()
    sheet_url = st.secrets["spreadsheet_url"]
    sh = client.open_by_url(sheet_url)
    worksheet = sh.worksheet(tab_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data), worksheet

# Φόρτωση Δεδομένων
try:
    df_customers, ws_customers = load_tab("Customers")
    df_transactions, ws_transactions = load_tab("Transactions")
except Exception as e:
    st.error(f"Σφάλμα σύνδεσης: {e}")
    st.stop()

# --- SIDEBAR: ΕΠΙΛΟΓΗ ΡΟΛΟΥ ---
st.sidebar.title("⚙️ Πλοήγηση")
user_role = st.sidebar.radio("Είστε:", ["📱 Πελάτης", "🔒 Διαχειριστής"])

# ==========================================
# 📱 1. ΠΡΟΒΟΛΗ ΠΕΛΑΤΗ (CUSTOMER MODE)
# ==========================================
if user_role == "📱 Πελάτης":
    st.title("🧺 ImatioApp - Παρακολούθηση Παραγγελίας")
    st.write("Εισάγετε τον αριθμό του κινητού σας για να δείτε την κατάσταση των ρούχων σας.")

    user_phone = st.text_input("📞 Αριθμός Κινητού Τηλεφώνου", placeholder="π.χ. 6912345678").strip()

    if st.button("🔎 Αναζήτηση Παραγγελίας", type="primary"):
        if not user_phone:
            st.warning("Παρακαλώ εισάγετε έναν αριθμό τηλεφώνου.")
        else:
            phone_col = 'Mobile' if 'Mobile' in df_customers.columns else 'Phone'
            
            df_customers[phone_col] = df_customers[phone_col].astype(str).str.strip()
            matched_customer = df_customers[df_customers[phone_col] == user_phone]

            if matched_customer.empty:
                st.error("❌ Δεν βρέθηκε παραγγελία καταχωρημένη με αυτό το τηλέφωνο.")
            else:
                cust_id = matched_customer['CustomerID'].values[0]
                cust_name = matched_customer['Name'].values[0]

                st.success(f"Γεια σας, **{cust_name}**! 👋")

                user_orders = df_transactions[df_transactions['CustomerID'] == cust_id]

                if user_orders.empty:
                    st.info("Δεν υπάρχουν καταχωρημένες παραγγελίες.")
                else:
                    st.subheader("📦 Οι Παραγγελίες σας")
                    for _, row in user_orders.iterrows():
                        status = row.get('Status', 'Προς επεξεργασία')
                        
                        if status == "Έτοιμος για παραλαβή":
                            badge = "🟢 **ΕΤΟΙΜΟΣ ΓΙΑ ΠΑΡΑΛΑΒΗ**"
                        elif status == "Προς φύλαξη":
                            badge = "🔵 **ΠΡΟΣ ΦΥΛΑΞΗ**"
                        elif status == "Παραδόθηκε":
                            badge = "⚪ **ΠΑΡΑΔΟΘΗΚΕ**"
                        else:
                            badge = "🟠 **ΠΡΟΣ ΕΠΕΞΕΡΓΑΣΙΑ**"

                        with st.expander(f"Παραγγελία #{int(row['TransactionID'])} - {badge}"):
                            st.write(f"👕 **Είδη / Περιγραφή:** {row.get('Item', '-')}")
                            st.write(f"💶 **Συνολικό Κόστος:** {row.get('TotalPrice', 0)}€")
                            st.write(f"📅 **Ημερομηνία Καταχώρησης:** {row.get('Date', '-')}")


# ==========================================
# 🔒 2. ΠΡΟΒΟΛΗ ΔΙΑΧΕΙΡΙΣΤΗ (ADMIN MODE - GOOGLE OAUTH)
# ==========================================
else:
    st.sidebar.divider()
    
    # Έλεγχος αν ο χρήστης είναι συνδεδεμένος μέσω Google OAuth
    if not st.experimental_user.is_logged_in:
        st.subheader("🔒 Περιοχή Διαχειριστή")
        st.info("Παρακαλώ συνδεθείτε με τον λογαριασμό Google για πρόσβαση.")
        if st.button("🔑 Σύνδεση με Google", type="primary"):
            st.login()
    else:
        user_email = st.experimental_user.email
        admin_email = st.secrets["auth"].get("admin_email", "")

        # Έλεγχος αν το email του χρήστη έχει δικαιώματα Admin
        if user_email.lower() != admin_email.lower():
            st.error(f"❌ Ο λογαριασμός **{user_email}** δεν έχει δικαιώματα διαχειριστή.")
            if st.button("🚪 Αποσύνδεση"):
                st.logout()
        else:
            st.sidebar.write(f"👤 **{st.experimental_user.name}**")
            st.sidebar.caption(f"({user_email})")
            if st.sidebar.button("🚪 Αποσύνδεση"):
                st.logout()

            st.title("🧺 ImatioApp - Διαχείριση (Admin)")

            # --- ΝΕΑ ΠΑΡΑΓΓΕΛΙΑ ---
            with st.form("new_order_form", clear_on_submit=True):
                st.subheader("➕ Νέα Παραγγελία")

                customer_list = ["-- Νέος Πελάτης --"]
                if not df_customers.empty and 'Name' in df_customers.columns:
                    phone_col = 'Mobile' if 'Mobile' in df_customers.columns else 'Phone'
                    customer_list += [f"{row['Name']} ({row[phone_col]})" for _, row in df_customers.iterrows() if pd.notnull(row['Name'])]

                selected_customer = st.selectbox("Επιλογή Πελάτη", customer_list)

                new_name, new_phone = "", ""
                if selected_customer == "-- Νέος Πελάτης --":
                    new_name = st.text_input("Όνομα Νέου Πελάτη")
                    new_phone = st.text_input("Τηλέφωνο Νέου Πελάτη")

                items_desc = st.text_area("Περιγραφή / Είδη")
                price = st.number_input("Συνολικό Κόστος (€)", min_value=0.0, step=0.50)
                initial_status = st.selectbox("Αρχική Κατάσταση", STATUS_OPTIONS, index=1)

                submit_order = st.form_submit_button("Καταχώρηση Παραγγελίας")

                if submit_order:
                    if selected_customer == "-- Νέος Πελάτης --":
                        if not new_name or not new_phone:
                            st.error("Συμπληρώστε όνομα και τηλέφωνο.")
                            st.stop()

                        cust_id = 1 if df_customers.empty or 'CustomerID' not in df_customers.columns else int(df_customers['CustomerID'].max()) + 1
                        ws_customers.append_row([cust_id, new_name, "", "", "", str(new_phone).strip(), "", ""])
                    else:
                        cust_name_display = selected_customer.split(" (")[0]
                        cust_id = int(df_customers[df_customers['Name'] == cust_name_display]['CustomerID'].values[0])

                    trans_id = 1 if df_transactions.empty or 'TransactionID' not in df_transactions.columns else int(df_transactions['TransactionID'].max()) + 1
                    today_str = datetime.now().strftime("%Y-%m-%d %H:%M")

                    ws_transactions.append_row([trans_id, cust_id, items_desc, price, initial_status, today_str])

                    st.success(f"✅ Η παραγγελία #{trans_id} καταχωρήθηκε!")
                    st.rerun()

            # --- ΕΝΕΡΓΕΣ ΠΑΡΑΓΓΕΛΙΕΣ ---
            st.divider()
            st.subheader("📋 Ενεργές Παραγγελίες")

            if not df_transactions.empty and 'Status' in df_transactions.columns:
                active_orders = df_transactions[df_transactions['Status'] != 'Παραδόθηκε']

                if active_orders.empty:
                    st.info("Δεν υπάρχουν εκκρεμείς παραγγελίες.")
                else:
                    for idx, row in active_orders.iterrows():
                        cust_info = df_customers[df_customers['CustomerID'] == row['CustomerID']]
                        c_name = cust_info['Name'].values[0] if not cust_info.empty else "Άγνωστος"

                        phone_val = "-"
                        if not cust_info.empty:
                            p_col = 'Mobile' if 'Mobile' in cust_info.columns else 'Phone'
                            phone_val = cust_info[p_col].values[0] if pd.notnull(cust_info[p_col].values[0]) else "-"

                        with st.expander(f"📦 #{int(row['TransactionID'])} - {c_name} ({row.get('Status', 'Προς επεξεργασία')})"):
                            st.write(f"📞 **Τηλέφωνο:** {phone_val}")
                            st.write(f"👕 **Είδη:** {row['Item']}")
                            st.write(f"💶 **Κόστος:** {row['TotalPrice']}€")
                            st.write(f"📅 **Ημερομηνία:** {row['Date']}")

                            curr_st = row.get('Status', 'Προς επεξεργασία')
                            new_st = st.selectbox(
                                "Αλλαγή Κατάστασης", 
                                STATUS_OPTIONS, 
                                index=STATUS_OPTIONS.index(curr_st) if curr_st in STATUS_OPTIONS else 1, 
                                key=f"st_{row['TransactionID']}"
                            )

                            if new_st != curr_st:
                                cell = ws_transactions.find(str(row['TransactionID']))
                                status_col_idx = df_transactions.columns.get_loc("Status") + 1
                                ws_transactions.update_cell(cell.row, status_col_idx, new_st)
                                st.toast(f"Ενημερώθηκε σε '{new_st}'")
                                st.rerun()
