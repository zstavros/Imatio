import streamlit as st
import pandas as pd

def render_admin_egg_dashboard(load_tab_data, get_worksheet):
    # CSS για μηδενισμό περιθωρίων και ομοιομορφία
    st.markdown("""
        <style>
        header {display: none !important;}
        [data-testid="stHeader"] {display: none !important; height: 0px !important;}
        [data-testid="stToolbar"] {display: none !important;}
        footer {display: none !important;}
        
        .block-container {
            padding-top: 0rem !important;
            margin-top: 0rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            padding-bottom: 0rem !important;
        }
        
        [data-baseweb="tab"] p {
            font-size: 1.2rem !important;
            font-weight: 600 !important;
        }
        [data-baseweb="tab"] {
            font-size: 1.2rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

    df_customers = load_tab_data("Customers")
    df_items = load_tab_data("Items")

    tab_c, tab_i, tab_x = st.tabs(["👥 Πελάτες", "👕 Είδη", "🧺 Χαλιά"])

    # --- 1. ΠΕΛΑΤΕΣ ---
    with tab_c:
        r_col1, r_col2 = st.columns([0.35, 0.65])
        with r_col1:
            st.markdown("<p style='margin-top: 4px; margin-bottom: 0px; font-weight: bold; font-size: 1.15rem;'>👥 ΠΕΛΑΤΕΣ</p>", unsafe_allow_html=True)
        with r_col2:
            customer_mode = st.radio("👥 ΠΕΛΑΤΕΣ", ["Νέος Πελάτης", "Επεξεργασία Υπάρχοντος"], horizontal=True, key="c_mode_radio", label_visibility="collapsed")

        ws_customers = get_worksheet("Customers")

        if customer_mode == "Νέος Πελάτης":
            with st.form("new_customer_form", clear_on_submit=True):
                n_name = st.text_input("Ονοματεπώνυμο *")
                n_mobile1 = st.text_input("Κινητό-1 (CuPhone)")
                n_mobile2 = st.text_input("Κινητό-2 (CuMobile)")
                n_address = st.text_input("Διεύθυνση (CuAddress)")
                n_email = st.text_input("Email (CuEmail)")
                n_notes = st.text_area("Σημειώσεις (CuNotes)")
                
                if st.form_submit_button("💾 Αποθήκευση Νέου Πελάτη", type="primary"):
                    if not n_name.strip():
                        st.error("❌ Παρακαλώ συμπληρώστε Όνομα.")
                    else:
                        cust_id = 1 if df_customers.empty or 'CustomerID' not in df_customers.columns else int(pd.to_numeric(df_customers['CustomerID'], errors='coerce').max() or 0) + 1
                        ws_customers.append_row([
                            cust_id, n_name.strip(), n_address.strip(), "", str(n_mobile1).strip(), str(n_mobile2).strip(), n_email.strip(), n_notes.strip()
                        ])
                        st.success(f"✅ Ο πελάτης **{n_name}** αποθηκεύτηκε επιτυχώς!")
                        st.cache_data.clear()
                        st.rerun()
        else:
            name_col = 'CuName' if 'CuName' in df_customers.columns else 'Name'
            if not df_customers.empty and name_col in df_customers.columns:
                valid_customers = df_customers[df_customers[name_col].astype(str).str.strip() != ""]
                cust_options = ["-- Επιλέξτε πελάτη για επεξεργασία --"] + [f"{r[name_col]} ({r.get('CuPhone', r.get('CuMobile', ''))})" for _, r in valid_customers.iterrows()]
                selected_c = st.selectbox("Αναζήτηση Πελάτη", cust_options, label_visibility="collapsed")

                if selected_c and selected_c != "-- Επιλέξτε πελάτη για επεξεργασία --":
                    c_name_val = selected_c.split(" (")[0]
                    c_row_data = valid_customers[valid_customers[name_col] == c_name_val].iloc[0]
                    
                    st.markdown("<hr style='margin: 8px 0px;'>", unsafe_allow_html=True)
                    with st.form("edit_customer_form"):
                        st.write(f"✏️ Επεξεργασία: **{c_name_val}**")
                        e_name = st.text_input("Ονοματεπώνυμο", value=str(c_row_data.get('CuName', c_row_data.get('Name', ''))))
                        e_mobile1 = st.text_input("Κινητό-1", value=str(c_row_data.get('CuPhone', '')))
                        e_mobile2 = st.text_input("Κινητό-2", value=str(c_row_data.get('CuMobile', '')))
                        e_address = st.text_input("Διεύθυνση", value=str(c_row_data.get('CuAddress', '')))
                        e_email = st.text_input("Email", value=str(c_row_data.get('CuEmail', '')))
                        e_notes = st.text_area("Σημειώσεις", value=str(c_row_data.get('CuNotes', '')))
                        
                        if st.form_submit_button("🔄 Ενημέρωση Στοιχείων"):
                            try:
                                cell = ws_customers.find(c_name_val)
                                ws_customers.update_cell(cell.row, df_customers.columns.get_loc(name_col) + 1, e_name)
                                ws_customers.update_cell(cell.row, 5, e_mobile1)
                                ws_customers.update_cell(cell.row, 6, e_mobile2)
                                ws_customers.update_cell(cell.row, 3, e_address)
                                ws_customers.update_cell(cell.row, 7, e_email)
                                ws_customers.update_cell(cell.row, 8, e_notes)
                                st.success("✅ Ενημερώθηκε!")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Σφάλμα: {e}")

    # --- 2. ΕΙΔΗ ---
    with tab_i:
        r_col1, r_col2 = st.columns([0.35, 0.65])
        with r_col1:
            st.markdown("<p style='margin-top: 4px; margin-bottom: 0px; font-weight: bold; font-size: 1.15rem;'>👕 ΕΙΔΗ</p>", unsafe_allow_html=True)
        with r_col2:
            item_mode = st.radio("👕 ΕΙΔΗ", ["Νέο Είδος", "Επεξεργασία"], horizontal=True, key="i_mode", label_visibility="collapsed")
            
        ws_items = get_worksheet("Items")
        if item_mode == "Νέο Είδος":
            with st.form("new_item_form", clear_on_submit=True):
                it_name = st.text_input("Όνομα Είδους (π.χ. Μπουφάν)")
                it_desc = st.text_input("Περιγραφή / Κατηγορία")
                if st.form_submit_button("Προσθήκη Είδους"):
                    if not it_name:
                        st.error("Βάλτε όνομα.")
                    else:
                        item_id = 1 if df_items.empty or 'ItemID' not in df_items.columns else int(df_items['ItemID'].max()) + 1
                        ws_items.append_row([item_id, it_name, it_desc])
                        st.success("Προστέθηκε!")
                        st.cache_data.clear()
                        st.rerun()
        else:
            col_name_key = 'ItName' if 'ItName' in df_items.columns else 'Name'
            if not df_items.empty and col_name_key in df_items.columns:
                valid_items = df_items[df_items[col_name_key].astype(str).str.strip() != ""]
                item_options = ["-- Επιλέξτε είδος --"] + valid_items[col_name_key].dropna().tolist()
                selected_it = st.selectbox("Αναζήτηση Είδους", item_options, label_visibility="collapsed", key="search_item_selectbox")

                if selected_it and selected_it != "-- Επιλέξτε είδος --":
                    with st.form("edit_item_form"):
                        st.write(f"✏️ Επεξεργασία: **{selected_it}**")
                        new_it_name = st.text_input("Όνομα Είδους", value=selected_it)
                        if st.form_submit_button("Αποθήκευση Αλλαγών"):
                            cell = ws_items.find(selected_it)
                            ws_items.update_cell(cell.row, df_items.columns.get_loc(col_name_key) + 1, new_it_name)
                            st.success("Ενημερώθηκε!")
                            st.cache_data.clear()
                            st.rerun()

    # --- 3. ΧΑΛΙΑ ---
    with tab_x:
        st.info("ℹ️ Χρησιμοποιείται η κεντρική βάση ειδών (Items) για καταχώρηση χαλιών.")
