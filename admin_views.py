import streamlit as st
import pandas as pd
from datetime import datetime

STATUS_OPTIONS = [
    "Έτοιμος για παραλαβή",
    "Προς επεξεργασία",
    "Προς φύλαξη",
    "Παραδόθηκε"
]

def render_admin_dashboard(load_tab_data, get_worksheet):
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
        "📝 Νέα Παράδοση", 
        "📋 Ανοιχτά", 
        "👥 Πελάτες", 
        "👕 Είδη", 
        "🧺 Χαλιά"
    ])

    # --- 1. ΝΕΑ ΠΑΡΑΔΟΣΗ ---
    with tab1:
        st.write("### 📝 Νέα Παράδοση / Συναλλαγή")
        with st.form("new_transaction_form", clear_on_submit=True):
            category_type = st.selectbox("Κατηγορία", ["👕 Ρούχα (TrItems)", "🧺 Χαλιά (TrXalia)"])

            name_col = 'CuName' if 'CuName' in df_customers.columns else 'Name'
            if df_customers.empty or name_col not in df_customers.columns:
                st.warning("Πρώτα καταχωρήστε πελάτες στην καρτέλα 'Πελάτες'.")
                st.stop()
            
            cust_choices = []
            for _, row in df_customers.iterrows():
                if pd.notnull(row.get(name_col)) and str(row.get(name_col)).strip() != '':
                    phone = row.get('CuMobile') if pd.notnull(row.get('CuMobile')) and str(row.get('CuMobile')).strip() != '' else row.get('CuPhone', '')
                    cust_choices.append(f"{row[name_col]} ({phone})")

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
                cust_id = int(df_customers[df_customers[name_col] == cust_name_clean]['CustomerID'].values[0])
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

    # --- 2. ΑΝΟΙΧΤΑ ---
    with tab2:
        st.write("### 📋 Εκκρεμή / Ανοιχτά προς παράδοση")
        sub_tab_c, sub_tab_x = st.tabs(["👕 Ρούχα", "🧺 Χαλιά"])

        with sub_tab_c:
            _render_active_list(df_tr_items, df_customers, "TrItems", get_worksheet)

        with sub_tab_x:
            _render_active_list(df_tr_xalia, df_customers, "TrXalia", get_worksheet)

    # --- 3. ΠΕΛΑΤΕΣ ---
    with tab3:
        st.write("### Διαχείριση Πελατών")
        customer_mode = st.radio("Επιλογή:", ["Νέος Πελάτης", "Επεξεργασία Υπάρχοντος"], horizontal=True, key="c_mode_radio")
        ws_customers = get_worksheet("Customers")

        if customer_mode == "Νέος Πελάτης":
            with st.form("new_customer_form", clear_on_submit=True):
                n_name = st.text_input("Ονοματεπώνυμο *")
                n_phone = st.text_input("Τηλέφωνο (CuPhone)")
                n_mobile = st.text_input("Κινητό (CuMobile)")
                n_address = st.text_input("Διεύθυνση (CuAddress)")
                
                if st.form_submit_button("💾 Αποθήκευση Νέου Πελάτη", type="primary"):
                    if not n_name.strip():
                        st.error("❌ Παρακαλώ συμπληρώστε Όνομα.")
                    else:
                        cust_id = 1 if df_customers.empty or 'CustomerID' not in df_customers.columns else int(pd.to_numeric(df_customers['CustomerID'], errors='coerce').max() or 0) + 1
                        ws_customers.append_row([cust_id, n_name.strip(), n_address.strip(), "", str(n_phone).strip(), str(n_mobile).strip(), "", ""])
                        st.success(f"✅ Ο πελάτης **{n_name}** αποθηκεύτηκε επιτυχώς!")
                        st.cache_data.clear()
                        st.rerun()

        else:
            name_col = 'CuName
