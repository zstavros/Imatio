import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# 1. NEA EGGRAFI PELATI
# ---------------------------------------------------------
def render_new_customer_tab(df_customers, get_worksheet):
    ws_customers = get_worksheet("Customers")

    with st.form("new_customer_form", clear_on_submit=True):
        col_nav, col_empty, col_save = st.columns([1, 1, 1])
        
        with col_nav:
            if st.form_submit_button("🏠 ARXIKI", use_container_width=True):
                st.session_state['active_subview'] = 'menu'
                st.rerun()

        with col_save:
            submitted = st.form_submit_button("💾 APO8IKEYSI", type="primary", use_container_width=True)

        st.markdown("### ➕ Nea Eggrafi Pelati")
        
        n_name = st.text_input("Onomatepwnymo *")
        n_mobile1 = st.text_input("Kinito-1 (CuPhone)")
        n_mobile2 = st.text_input("Kinito-2 (CuMobile)")
        n_address = st.text_input("Dieythynsi (CuAddress)")
        n_city = st.text_input("Poli (CuCity)")
        n_email = st.text_input("Email (CuEmail)")
        n_notes = st.text_area("Simeioseis (CuNotes)")
        
        if submitted:
            if not n_name.strip():
                st.error("❌ Parakalw symplirwste Onoma.")
            else:
                cust_id = 1 if df_customers.empty or 'CustomerID' not in df_customers.columns else int(pd.to_numeric(df_customers['CustomerID'], errors='coerce').max() or 0) + 1
                ws_customers.append_row([
                    cust_id, n_name.strip(), n_address.strip(), n_city.strip(), str(n_mobile1).strip(), str(n_mobile2).strip(), n_email.strip(), n_notes.strip()
                ])
                st.success(f"✅ O pelatis **{n_name}** apothikeytike epityxws!")
                st.cache_data.clear()
                st.rerun()

# ---------------------------------------------------------
# 2. TROPOPOISI PELATI
# ---------------------------------------------------------
def render_edit_customer_tab(df_customers, get_worksheet):
    col_nav, col_space = st.columns([1, 2])
    with col_nav:
        if st.button("🏠 ARXIKI", key="back_home_edit_cust", use_container_width=True):
            st.session_state['active_subview'] = 'menu'
            st.rerun()

    st.markdown("### ✏️ Tropopoiisi Stoixeiwn Pelati")
    ws_customers = get_worksheet("Customers")
    name_col = 'CuName' if 'CuName' in df_customers.columns else 'Name'

    if not df_customers.empty and name_col in df_customers.columns:
        valid_customers = df_customers[df_customers[name_col].astype(str).str.strip() != ""]
        cust_options = ["-- Epilexte pelati gia epexergasia --"] + [f"{r[name_col]} ({r.get('CuPhone', r.get('CuMobile', ''))})" for _, r in valid_customers.iterrows()]
        selected_c = st.selectbox("Anazitisi Pelati", cust_options, label_visibility="collapsed")

        if selected_c and selected_c != "-- Epilexte pelati gia epexergasia --":
            c_name_val = selected_c.split(" (")[0]
            c_row_data = valid_customers[valid_customers[name_col] == c_name_val].iloc[0]
            
            st.markdown("<hr style='margin: 8px 0px;'>", unsafe_allow_html=True)
            with st.form("edit_customer_form"):
                st.write(f"✏️ Epexergasia: **{c_name_val}**")
                e_name = st.text_input("Onomatepwnymo", value=str(c_row_data.get('CuName', c_row_data.get('Name', ''))))
                e_mobile1 = st.text_input("Kinito-1", value=str(c_row_data.get('CuPhone', '')))
                e_mobile2 = st.text_input("Kinito-2", value=str(c_row_data.get('CuMobile', '')))
                e_address = st.text_input("Dieythynsi", value=str(c_row_data.get('CuAddress', '')))
                e_city = st.text_input("Poli", value=str(c_row_data.get('CuCity', '')))
                e_email = st.text_input("Email", value=str(c_row_data.get('CuEmail', '')))
                e_notes = st.text_area("Simeioseis", value=str(c_row_data.get('CuNotes', '')))
                
                if st.form_submit_button("🔄 Enimerosi Stoixeiwn", type="primary"):
                    try:
                        cell = ws_customers.find(c_name_val)
                        ws_customers.update_cell(cell.row, df_customers.columns.get_loc(name_col) + 1, e_name)
                        ws_customers.update_cell(cell.row, 5, e_mobile1)
                        ws_customers.update_cell(cell.row, 6, e_mobile2)
                        ws_customers.update_cell(cell.row, 3, e_address)
                        ws_customers.update_cell(cell.row, 4, e_city)
                        ws_customers.update_cell(cell.row, 7, e_email)
                        ws_customers.update_cell(cell.row, 8, e_notes)
                        st.success("✅ Enimerwthike!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Sfalma: {e}")

# ---------------------------------------------------------
# 3. ΝΕΟ ΕΙΔΟΣ ΚΑΤΑΛΟΓΟΥ
# ---------------------------------------------------------
def render_new_item_tab(df_items, get_worksheet):
    ws_items = get_worksheet("Items")

    with st.form("new_item_form", clear_on_submit=True):
        col_nav, col_empty, col_save = st.columns([1, 1, 1])
        
        with col_nav:
            if st.form_submit_button("🏠 ΑΡΧΙΚΗ", use_container_width=True):
                st.session_state['active_subview'] = 'menu'
                st.rerun()

        with col_save:
            submitted = st.form_submit_button("💾 ΑΠΟΘΗΚΕΥΣΗ", type="primary", use_container_width=True)

        st.markdown("### ➕ Νέο Είδος Καταλόγου")
        
        it_name = st.text_input("Όνομα Είδους (π.χ. Μπουφάν)")
        
        # Επιλογή κατηγορίας αποκλειστικά ανάμεσα σε Ρούχα και Χαλιά
        it_desc = st.selectbox("Περιγραφή / Κατηγορία", ["Ρούχα", "Χαλιά"])
        
        it_price = st.number_input("ΤΙΜΗ (€)", min_value=0.0, step=0.5)
        it_price_m2 = st.number_input("ΤΙΜΗ ΤΕΤΡΑΓΩΝΙΚΟΥ (€/m²)", min_value=0.0, step=0.5)
        
        if submitted:
            if not it_name:
                st.error("Βάλτε όνομα είδους.")
            else:
                item_id = 1 if df_items.empty or 'ItemID' not in df_items.columns else int(pd.to_numeric(df_items['ItemID'], errors='coerce').max() or 0) + 1
                ws_items.append_row([item_id, it_name, it_desc, it_price, it_price_m2])
                st.success("Το είδος προστέθηκε επιτυχώς!")
                st.cache_data.clear()
                st.rerun()

# ---------------------------------------------------------
# 4. TROPOPOISI KATALOGOY
# ---------------------------------------------------------
def render_edit_item_tab(df_items, get_worksheet):
    col_nav, col_space = st.columns([1, 2])
    with col_nav:
        if st.button("🏠 ARXIKI", key="back_home_edit_item", use_container_width=True):
            st.session_state['active_subview'] = 'menu'
            st.rerun()

    st.markdown("### ✏️ Tropopoiisi Katalogoy")
    ws_items = get_worksheet("Items")
    col_name_key = 'ItName' if 'ItName' in df_items.columns else 'Name'

    if df_items.empty or col_name_key not in df_items.columns:
        st.info("Den yparxoun apothikeymena eidi.")
    else:
        valid_items = df_items[df_items[col_name_key].astype(str).str.strip() != ""]
        item_options = ["-- Epilexte eidos --"] + valid_items[col_name_key].dropna().tolist()
        selected_it = st.selectbox("Anazitisi Eidous", item_options, label_visibility="collapsed", key="search_item_selectbox")

        if selected_it and selected_it != "-- Epilexte eidos --":
            row_data = valid_items[valid_items[col_name_key] == selected_it].iloc[0]
            curr_price = float(row_data.get('Price', 0.0) or 0.0) if 'Price' in df_items.columns else 0.0
            curr_price_m2 = float(row_data.get('Price m2', row_data.get('Price_m2', 0.0)) or 0.0)

            with st.form("edit_item_form"):
                st.write(f"✏️ Epexergasia: **{selected_it}**")
                new_it_name = st.text_input("Onoma Eidous", value=selected_it)
                new_price = st.number_input("TIMI (€)", value=curr_price, min_value=0.0, step=0.5)
                new_price_m2 = st.number_input("TIMI TETRAGWNIKOY (€/m²)", value=curr_price_m2, min_value=0.0, step=0.5)
                
                if st.form_submit_button("Apothikeysi Allagwn", type="primary"):
                    try:
                        cell = ws_items.find(selected_it)
                        ws_items.update_cell(cell.row, 2, new_it_name)
                        ws_items.update_cell(cell.row, 3, new_price)
                        ws_items.update_cell(cell.row, 4, new_price_m2)
                        st.success("✅ To eidos enimerwthike epityxws!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Sfalma: {e}")
