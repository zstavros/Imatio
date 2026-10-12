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

st.markdown("""
    <style>
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {display: none !important;}
    footer {visibility: hidden !important;}
    .block-container { padding-top: 2.5rem !important; }
    </style>
""", unsafe_allow_html=True)

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

def _render_active_list(df_trans, df_cust, sheet_name):
    if df_trans.empty or 'Status' not in df_trans.columns:
        st.info("Δεν υπάρχουν εγγραφές.")
        return

    active_data = df_trans[df_trans['Status'] != 'Παραδόθηκε']
    if active_data.empty:
        st.info("Δεν υπάρχουν εκκρεμότητες.")
        return

    ws = get_worksheet(sheet_name)
    for _, row in active_data.iterrows():
        cust_info = df_cust[df_cust['CustomerID'] == row['CustomerID']]
        c_name = cust_info['Name'].values[0] if not cust_info.empty else "Άγνωστος"

        with st.expander(f"#{int(row['TransactionID'])} - {c_name} | {row.get('ItName', '')}"):
            st.write(f"📍 **Θέση:** {row.get('Place', '-')}")
            st.write(f"💶 **Κόστος:** {row.get('TotalPrice', 0)}€")

            curr_st = row.get('Status', 'Προς επεξεργασία')
            new_st = st.selectbox(
                "Αλλαγή Κατάστασης", STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(curr_st) if curr_st in STATUS_OPTIONS else 1,
                key=f"st_{sheet_name}_{row['TransactionID']}"
            )
            if new_st != curr_st:
                cell = ws.find(str(row['TransactionID']))
                status_col_idx = df_trans.columns.get_loc("Status") + 1
                ws.update_cell(cell.row, status_col_idx, new_st)
                if new_st == "Παραδόθηκε":
                    date_out_idx = df_trans.columns.get_loc("DateOut") + 1
                    ws.update_cell(cell.row, date_out_idx, datetime.now().strftime("%Y-%m-%d %H:%M"))
                st.toast("Ενημερώθηκε!")
                st.cache_data.clear()
                st.rerun()

# Έλεγχος αν ο διαχειριστής είναι συνδεδεμένος
is_admin_logged_in = st.session_state.get("admin_logged_in", False)

if not is_admin_logged_in:
    st.title("🧺 ImatioApp")
    user_role = st.radio("Επιλέξτε ρόλο:", ["📱 Πελάτης", "🔒 Διαχειριστής"], horizontal=True)
    st.divider()
else:
    user_role = "🔒 Διαχειριστής"

# ==========================================
# 📱 ΠΕΛΑΤΗΣ
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

            phone_col = 'Mobile' if 'Mobile' in df_customers.columns else 'Phone'
            df_customers[phone_col] = df_customers[phone_col].astype(str).str.strip()
            matched_customer = df_customers[df_customers[phone_col] == user_phone]

            if matched_customer.empty:
                st.error("❌ Δεν βρέθηκε πελάτης με αυτό το τηλέφωνο.")
            else:
                cust_id = matched_customer['CustomerID'].values[0]
                cust_name = matched_customer['Name'].values[0]
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
# 🔒 ΔΙΑΧΕΙΡΙΣΤΗΣ
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
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            st.markdown("### 🛠️ Πίνακας Ελέγχου")
        with col2:
            if st.button("🚪 Έξοδος"):
                st.session_state.admin_logged_in = False
                st.cache_data.clear()
                st.rerun()

        df_customers = load_tab_data("Customers")
        df_items = load_tab_data("Items")
        df_tr_items = load_tab_data("TrItems")
        df_tr_xalia = load_tab_data("TrXalia")

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "👥 Πελάτης", 
            "👕 Είδη", 
            "🧺 Χαλιά", 
            "📝 Νέα Παράδοση", 
            "📋 Ανοιχτά"
        ])

        # 1. ΠΕΛΑΤΗΣ
        with tab1:
            st.write("### Διαχείριση Πελατών")
            customer_mode = st.radio("Επιλογή:", ["Νέος Πελάτης", "Επεξεργασία Υπάρχοντος"], horizontal=True, key="c_mode")
            ws_customers = get_worksheet("Customers")

            if customer_mode == "Νέος Πελάτης":
                with st.form("new_customer_form", clear_on_submit=True):
                    n_name = st.text_input("Ονοματεπώνυμο")
                    n_phone = st.text_input("Κινητό Τηλέφωνο")
                    n_address = st.text_input("Διεύθυνση (Προαιρετικά)")
                    
                    if st.form_submit_button("Αποθήκευση Νέου Πελάτη"):
                        if not n_name or not n_phone:
                            st.error("Συμπληρώστε όνομα και τηλέφωνο.")
                        else:
                            cust_id = 1 if df_customers.empty or 'CustomerID' not in df_customers.columns else int(df_customers['CustomerID'].max()) + 1
                            ws_customers.append_row([cust_id, n_name, n_address, "", "", str(n_phone).strip(), "", ""])
                            st.success(f"Ο πελάτης {n_name} αποθηκεύτηκε!")
                            st.cache_data.clear()
                            st.rerun()
            else:
                if df_customers.empty or 'Name' not in df_customers.columns:
                    st.info("Δεν υπάρχουν πελάτες.")
                else:
                    cust_options = [f"{row['Name']} ({row.get('Mobile', row.get('Phone', ''))})" for _, row in df_customers.iterrows() if pd.notnull(row['Name'])]
                    selected_c = st.selectbox("Επιλέξτε πελάτη για επεξεργασία", cust_options)
                    if selected_c:
                        c_name_val = selected_c.split(" (")[0]
                        c_row_data = df_customers[df_customers['Name'] == c_name_val].iloc[0]
                        with st.form("edit_customer_form"):
                            e_name = st.text_input("Ονοματεπώνυμο", value=str(c_row_data.get('Name', '')))
                            e_phone = st.text_input("Κινητό Τηλέφωνο", value=str(c_row_data.get('Mobile', c_row_data.get('Phone', ''))))
                            if st.form_submit_button("Ενημέρωση Στοιχείων"):
                                cell = ws_customers.find(c_name_val)
                                name_col = df_customers.columns.get_loc("Name") + 1
                                phone_col = (df_customers.columns.get_loc("Mobile") if "Mobile" in df_customers.columns else df_customers.columns.get_loc("Phone")) + 1
                                ws_customers.update_cell(cell.row, name_col, e_name)
                                ws_customers.update_cell(cell.row, phone_col, e_phone)
                                st.success("Ενημερώθηκε με επιτυχία!")
                                st.cache_data.clear()
                                st.rerun()

        # 2. ΕΙΔΗ
        with tab2:
            st.write("### Διαχείριση Ειδών / Ρούχων (Items)")
            item_mode = st.radio("Επιλογή:", ["Νέο Είδος", "Επεξεργασία"], horizontal=True, key="i_mode")
            ws_items = get_worksheet("Items")

            if item_mode == "Νέο Είδος":
                with st.form("new_item_form", clear_on_submit=True):
                    it_name = st.text_input("Όνομα Είδους (π.χ. Μπουφάν, Κοστούμι)")
                    it_desc = st.text_input("Περιγραφή / Κατηγορία")
                    if st.form_submit_button("Προσθήκη Είδους"):
                        if not it_name:
                            st.error("Βάλτε όνομα είδους.")
                        else:
                            item_id = 1 if df_items.empty or 'ItemID' not in df_items.columns else int(df_items['ItemID'].max()) + 1
                            ws_items.append_row([item_id, it_name, it_desc])
                            st.success("Το είδος προστέθηκε!")
                            st.cache_data.clear()
                            st.rerun()
            else:
                col_name_key = 'ItName' if 'ItName' in df_items.columns else 'Name'
                if df_items.empty or col_name_key not in df_items.columns:
                    st.info("Δεν υπάρχουν αποθηκευμένα είδη.")
                else:
                    item_list = df_items[col_name_key].dropna().tolist()
                    selected_it = st.selectbox("Επιλέξτε Είδος", item_list)
                    if selected_it:
                        with st.form("edit_item_form"):
                            new_it_name = st.text_input("Όνομα Είδους", value=selected_it)
                            if st.form_submit_button("Αποθήκευση Αλλαγών"):
                                cell = ws_items.find(selected_it)
                                col_idx = df_items.columns.get_loc(col_name_key) + 1
                                ws_items.update_cell(cell.row, col_idx, new_it_name)
                                st.success("Ενημερώθηκε!")
                                st.cache_data.clear()
                                st.rerun()

        # 3. ΧΑΛΙΑ
        with tab3:
            st.write("### Διαχείριση Χαλιών")
            st.info("Χρησιμοποιείται η κεντρική βάση είδών (Items) για καταχώρηση χαλιών.")

        # 4. ΝΕΑ ΠΑΡΑΔΟΣΗ
        with tab4:
            st.write("### 📝 Νέα Παράδοση / Συναλλαγή")
            with st.form("new_transaction_form", clear_on_submit=True):
                category_type = st.selectbox("Κατηγορία", ["👕 Ρούχα (TrItems)", "🧺 Χαλιά (TrXalia)"])

                if df_customers.empty or 'Name' not in df_customers.columns:
                    st.warning("Πρώτα καταχωρήστε πελάτες στην καρτέλα 'Πελάτης'.")
                    st.stop()
                
                cust_choices = [f"{row['Name']} ({row.get('Mobile', row.get('Phone', ''))})" for _, row in df_customers.iterrows() if pd.notnull(row['Name'])]
                selected_customer_str = st.selectbox("Επιλογή Πελάτη", cust_choices)

                col_name_key = 'ItName' if 'ItName' in df_items.columns else 'Name'
                if df_items.empty or col_name_key not in df_items.columns:
                    item_name_input = st.text_input("Όνομα Είδους")
                else:
                    item_choices = df_items[col_name_key].dropna().tolist()
                    item_name_input = st.selectbox("Επιλογή Είδους από Καταχωρημένα", item_choices)

                place_val = st.text_input("Θέση / Ράφι (Place)")
                price = st.number_input("Συνολικό Κόστος (€)", min_value=0.0, step=0.50)
                initial_status = st.selectbox("Αρχική Κατάσταση", STATUS_OPTIONS, index=1)

                if st.form_submit_button("Καταχώρηση Νέας Παραλαβής"):
                    cust_name_clean = selected_customer_str.split(" (")[0]
                    cust_id = int(df_customers[df_customers['Name'] == cust_name_clean]['CustomerID'].values[0])
                    today_str = datetime.now().strftime("%Y-%m-%d %H:%M")

                    if "Ρούχα" in category_type:
                        ws_tr = get_worksheet("TrItems")
                        trans_id = 1 if df_tr_items.empty or 'TransactionID' not in df_tr_items.columns else int(df_tr_items['TransactionID'].max()) + 1
                        ws_tr.append_row([trans_id, cust_id, item_name_input, place_val, today_str, "", price, initial_status])
                    else:
                        ws_tr = get_worksheet("TrXalia")
                        trans_id = 1 if df_tr_xalia.empty or 'TransactionID' not in df_tr_xalia.columns else int(df_tr_xalia['TransactionID'].max()) + 1
                        ws_tr.append_row([trans_id, cust_id, item_name_input, place_val, today_str, "", price, initial_status])

                    st.success("✅ Η συναλλαγή καταχωρήθηκε επιτυχώς!")
                    st.cache_data.clear()
                    st.rerun()

        # 5. ΑΝΟΙΧΤΑ
        with tab5:
            st.write("### 📋 Εκκρεμή / Ανοιχτά προς παράδοση")
            sub_tab_c, sub_tab_x = st.tabs(["👕 Ρούχα", "🧺 Χαλιά"])

            with sub_tab_c:
                _render_active_list(df_tr_items, df_customers, "TrItems")

            with sub_tab_x:
                _render_active_list(df_tr_xalia, df_customers, "TrXalia")
