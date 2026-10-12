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
                n_mobile1 = st.text_input("Κινητό-1 ")
                n_mobile2 = st.text_input("Κινητό-2 ")
                n_address = st.text_input("Διεύθυνση ")
                n_email = st.text_input("Email ")
                n_notes = st.text_area("Σημειώσεις ")
                
                if st.form_submit_button("💾 Αποθήκευση Νέου Πελάτη", type="primary"):
                    if not n_name.strip():
                        st.error("❌ Παρακαλώ συμπληρώστε Όνομα.")
                    else:
                        cust_id = 1 if df_customers.empty or 'CustomerID' not in df_customers.columns else int(pd.to_numeric(df_customers['CustomerID'], errors='coerce').max() or 0) + 1
                        # Σειρά στηλών: CustomerID, CuName, CuAddress, CuCity, CuPhone(Κινητό-1), CuMobile(Κινητό-2), CuEmail, CuNotes
                        ws_customers.append_row([
                            cust_id, 
                            n_name.strip(), 
                            n_address.strip(), 
                            "", 
                            str(n_mobile1).strip(), 
                            str(n_mobile2).strip(), 
                            n_email.strip(), 
                            n_notes.strip()
                        ])
                        st.success(f"✅ Ο πελάτης **{n_name}** αποθηκεύτηκε επιτυχώς!")
                        st.cache_data.clear()
                        st.rerun()

        else:
            name_col = 'CuName' if 'CuName' in df_customers.columns else 'Name'
            if df_customers.empty or name_col not in df_customers.columns:
                st.warning("⚠️ Δεν βρέθηκαν καταχωρημένοι πελάτες.")
            else:
                st.write("🔍 **Γράψτε όνομα ή κινητό για άμεση ανεύρεση:**")
                search_query = st.text_input("Αναζήτηση πελάτη", placeholder="π.χ. Σταύρος ή 69...", label_visibility="collapsed")

                valid_customers = df_customers[df_customers[name_col].astype(str).str.strip() != ""]

                if search_query.strip() != "":
                    q = search_query.strip().lower()
                    phone_col = 'CuMobile' if 'CuMobile' in df_customers.columns else ('CuPhone' if 'CuPhone' in df_customers.columns else '')
                    
                    mask = valid_customers[name_col].astype(str).str.lower().str.contains(q)
                    if phone_col and phone_col in valid_customers.columns:
                        mask = mask | valid_customers[phone_col].astype(str).str.lower().str.contains(q)
                    
                    filtered_df = valid_customers[mask]
                else:
                    filtered_df = pd.DataFrame()

                if search_query.strip() == "":
                    st.info("👆 Πληκτρολογήστε μερικά γράμματα từ το όνομα ή το τηλέφωνο του πελάτη για να εμφανιστεί.")
                elif filtered_df.empty:
                    st.warning("❌ Δεν βρέθηκε πελάτης που να ταιριάζει με την αναζήτηση.")
                else:
                    cust_options = []
                    for _, row in filtered_df.iterrows():
                        phone = row.get('CuPhone') if pd.notnull(row.get('CuPhone')) and str(row.get('CuPhone')).strip() != '' else row.get('CuMobile', '')
                        cust_options.append(f"{row[name_col]} ({phone})")

                    selected_c = st.selectbox("Αποτελέσματα Αναζήτησης", cust_options, label_visibility="collapsed")

                    if selected_c:
                        c_name_val = selected_c.split(" (")[0]
                        c_row_data = filtered_df[filtered_df[name_col] == c_name_val].iloc[0]
                        
                        with st.form("edit_customer_form"):
                            st.write(f"✏️ Επεξεργασία πελάτη: **{c_name_val}**")
                            e_name = st.text_input("Ονοματεπώνυμο", value=str(c_row_data.get('CuName', c_row_data.get('Name', ''))))
                            e_mobile1 = st.text_input("Κινητό-1", value=str(c_row_data.get('CuPhone', '')))
                            e_mobile2 = st.text_input("Κινητό-2", value=str(c_row_data.get('CuMobile', '')))
                            e_address = st.text_input("Διεύθυνση", value=str(c_row_data.get('CuAddress', '')))
                            e_email = st.text_input("Email", value=str(c_row_data.get('CuEmail', '')))
                            e_notes = st.text_area("Σημειώσεις", value=str(c_row_data.get('CuNotes', '')))
                            
                            if st.form_submit_button("🔄 Ενημέρωση Στοιχείων"):
                                try:
                                    cell = ws_customers.find(c_name_val)
                                    
                                    name_col_idx = df_customers.columns.get_loc(name_col) + 1
                                    phone_col_idx = df_customers.columns.get_loc("CuPhone") + 1 if "CuPhone" in df_customers.columns else 5
                                    mobile_col_idx = df_customers.columns.get_loc("CuMobile") + 1 if "CuMobile" in df_customers.columns else 6
                                    address_col_idx = df_customers.columns.get_loc("CuAddress") + 1 if "CuAddress" in df_customers.columns else 3
                                    email_col_idx = df_customers.columns.get_loc("CuEmail") + 1 if "CuEmail" in df_customers.columns else 7
                                    notes_col_idx = df_customers.columns.get_loc("CuNotes") + 1 if "CuNotes" in df_customers.columns else 8
                                    
                                    ws_customers.update_cell(cell.row, name_col_idx, e_name)
                                    ws_customers.update_cell(cell.row, phone_col_idx, e_mobile1)
                                    ws_customers.update_cell(cell.row, mobile_col_idx, e_mobile2)
                                    ws_customers.update_cell(cell.row, address_col_idx, e_address)
                                    ws_customers.update_cell(cell.row, email_col_idx, e_email)
                                    ws_customers.update_cell(cell.row, notes_col_idx, e_notes)
                                    
                                    st.success("✅ Τα στοιχεία ενημερώθηκαν επιτυχώς!")
                                    st.cache_data.clear()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Σφάλμα: {e}")

    # --- 4. ΕΙΔΗ ---
    with tab4:
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

    # --- 5. ΧΑΛΙΑ ---
    with tab5:
        st.write("### Διαχείριση Χαλιών")
        st.info("Χρησιμοποιείται η κεντρική βάση είδών (Items) για καταχώρηση χαλιών.")


def _render_active_list(df_trans, df_cust, sheet_name, get_worksheet_fn):
    if df_trans.empty or 'Status' not in df_trans.columns:
        st.info("Δεν υπάρχουν εγγραφές.")
        return

    active_data = df_trans[df_trans['Status'] != 'Παραδόθηκε']
    if active_data.empty:
        st.info("Δεν υπάρχουν εκκρεμότητες.")
        return

    ws = get_worksheet_fn(sheet_name)
    name_col = 'CuName' if 'CuName' in df_cust.columns else 'Name'

    for _, row in active_data.iterrows():
        cust_info = df_cust[df_cust['CustomerID'] == row['CustomerID']]
        c_name = cust_info[name_col].values[0] if not cust_info.empty else "Άγνωστος"

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
