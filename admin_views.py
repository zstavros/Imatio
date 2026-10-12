# --- 1. NEA PARADOSI ---
    with tab1:
        st.write("### 📝 Νέα Παράδοση / Συναλλαγή")
        with st.form("new_transaction_form", clear_on_submit=True):
            category_type = st.selectbox("Κατηγορία", ["👕 Ρούχα (TrItems)", "🧺 Χαλιά (TrXalia)"])

            if df_customers.empty or 'CuName' not in df_customers.columns:
                st.warning("Πρώτα καταχωρήστε πελάτες στην καρτέλα 'Πελάτες'.")
                st.stop()
            
            # Xrisimopoiei tis στήλες CuName, CuPhone, CuMobile
            cust_choices = []
            for _, row in df_customers.iterrows():
                if pd.notnull(row.get('CuName')) and str(row.get('CuName')).strip() != '':
                    phone = row.get('CuMobile') if pd.notnull(row.get('CuMobile')) and str(row.get('CuMobile')).strip() != '' else row.get('CuPhone', '')
                    cust_choices.append(f"{row['CuName']} ({phone})")

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
                cust_id = int(df_customers[df_customers['CuName'] == cust_name_clean]['CustomerID'].values[0])
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

    # --- 3. PELATES ---
    with tab3:
        st.write("### Διαχείριση Πελατών")
        customer_mode = st.radio("Επιλογή:", ["Νέος Πελάτης", "Επεξεργασία Υπάρχοντος"], horizontal=True, key="c_mode_radio")
        ws_customers = get_worksheet("Customers")

        if customer_mode == "Νέος Πελάτης":
            with st.form("new_customer_form", clear_on_submit=True):
                n_name = st.text_input("Ονοματεπώνυμο *")
                n_phone = st.text_input("Τηλέφωνο (CuPhone) *")
                n_mobile = st.text_input("Κινητό (CuMobile)")
                n_address = st.text_input("Διεύθυνση (CuAddress)")
                
                if st.form_submit_button("💾 Αποθήκευση Νέου Πελάτη", type="primary"):
                    if not n_name.strip():
                        st.error("❌ Παρακαλώ συμπληρώστε Όνομα.")
                    else:
                        cust_id = 1 if df_customers.empty or 'CustomerID' not in df_customers.columns else int(pd.to_numeric(df_customers['CustomerID'], errors='coerce').max() or 0) + 1
                        # Katachorisi me tis σωστή σειρά των στηλών: CustomerID, CuName, CuAddress, CuCity, CuPhone, CuMobile, CuEmail, CuNotes
                        ws_customers.append_row([cust_id, n_name.strip(), n_address.strip(), "", str(n_phone).strip(), str(n_mobile).strip(), "", ""])
                        st.success(f"✅ Ο πελάτης **{n_name}** αποθηκεύτηκε επιτυχώς!")
                        st.cache_data.clear()
                        st.rerun()

        else:
            if df_customers.empty or 'CuName' not in df_customers.columns:
                st.warning("⚠️ Δεν βρέθηκαν καταχωρημένοι πελάτες.")
            else:
                valid_customers = df_customers[df_customers['CuName'].astype(str).str.strip() != ""]
                
                if valid_customers.empty:
                    st.info("ℹ️ Δεν υπάρχουν πελάτες.")
                else:
                    cust_options = []
                    for _, row in valid_customers.iterrows():
                        phone = row.get('CuMobile') if pd.notnull(row.get('CuMobile')) and str(row.get('CuMobile')).strip() != '' else row.get('CuPhone', '')
                        cust_options.append(f"{row['CuName']} ({phone})")

                    selected_c = st.selectbox("🔍 Επιλέξτε πελάτη για επεξεργασία", cust_options)
                    
                    if selected_c:
                        c_name_val = selected_c.split(" (")[0]
                        c_row_data = valid_customers[valid_customers['CuName'] == c_name_val].iloc[0]
                        
                        with st.form("edit_customer_form"):
                            e_name = st.text_input("Ονοματεπώνυμο", value=str(c_row_data.get('CuName', '')))
                            e_phone = st.text_input("Τηλέφωνο", value=str(c_row_data.get('CuPhone', '')))
                            e_mobile = st.text_input("Κινητό", value=str(c_row_data.get('CuMobile', '')))
                            e_address = st.text_input("Διεύθυνση", value=str(c_row_data.get('CuAddress', '')))
                            
                            if st.form_submit_button("🔄 Ενημέρωση Στοιχείων"):
                                try:
                                    cell = ws_customers.find(c_name_val)
                                    
                                    name_col_idx = df_customers.columns.get_loc("CuName") + 1
                                    phone_col_idx = df_customers.columns.get_loc("CuPhone") + 1
                                    mobile_col_idx = df_customers.columns.get_loc("CuMobile") + 1
                                    address_col_idx = df_customers.columns.get_loc("CuAddress") + 1
                                    
                                    ws_customers.update_cell(cell.row, name_col_idx, e_name)
                                    ws_customers.update_cell(cell.row, phone_col_idx, e_phone)
                                    ws_customers.update_cell(cell.row, mobile_col_idx, e_mobile)
                                    ws_customers.update_cell(cell.row, address_col_idx, e_address)
                                    
                                    st.success("✅ Τα στοιχεία ενημερώθηκαν επιτυχώς!")
                                    st.cache_data.clear()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Σφάλμα: {e}")
