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
                # Diavazoume ta frestka rows gia na vroume to sosto max ID
                all_vals = ws_customers.get_all_records()
                df_fresh = pd.DataFrame(all_vals)
                
                cust_id = 1 if df_fresh.empty or 'CustomerID' not in df_fresh.columns else int(pd.to_numeric(df_fresh['CustomerID'], errors='coerce').max() or 0) + 1
                
                ws_customers.append_row([
                    cust_id, n_name.strip(), n_address.strip(), n_city.strip(), str(n_mobile1).strip(), str(n_mobile2).strip(), n_email.strip(), n_notes.strip()
                ])
                
                st.cache_data.clear()
                st.session_state['active_subview'] = 'menu'
                st.rerun()

# ---------------------------------------------------------
# 2. TROPOPOISI PELATI (Diavazei AMESA freska dedomena)
# ---------------------------------------------------------
def render_edit_customer_tab(df_customers_old, get_worksheet):
    st.markdown("### ✏️ Tropopoiisi Stoixeiwn Pelati")
    ws_customers = get_worksheet("Customers")

    # Koumpiara stin koryfi
    col_nav, col_save = st.columns([1, 1])
    with col_nav:
        if st.button("🏠 ARXIKI", key="btn_home_edit_cust", use_container_width=True):
            st.session_state['active_subview'] = 'menu'
            st.rerun()
    with col_save:
        save_clicked = st.button("💾 APO8IKEYSI", key="btn_save_edit_cust", type="primary", use_container_width=True)

    st.markdown("<hr style='margin: 8px 0px;'>", unsafe_allow_html=True)

    # DIAVAZOYME FRESTKA DEDOMENA APO TO GOOGLE SHEET APEUTHEIAS!
    data = ws_customers.get_all_records()
    df_customers = pd.DataFrame(data)

    name_col = 'CuName' if 'CuName' in df_customers.columns else ('Name' if 'Name' in df_customers.columns else None)

    if df_customers.empty or not name_col:
        st.info("Den vrethikan apothikeymenoi pelates.")
        return

    valid_customers = df_customers[df_customers[name_col].astype(str).str.strip() != ""]
    cust_options = ["-- Epilexte pelati gia epexergasia --"] + [f"{r[name_col]} ({r.get('CuPhone', r.get('CuMobile', ''))})" for _, r in valid_customers.iterrows()]
    
    selected_c = st.selectbox("Anazitisi Pelati", cust_options, label_visibility="collapsed", key="search_cust_selectbox")

    if selected_c and selected_c != "-- Epilexte pelati gia epexergasia --":
        c_name_val = selected_c.split(" (")[0]
        c_row_data = valid_customers[valid_customers[name_col] == c_name_val].iloc[0]
        
        st.markdown(f"✏️ Epexergasia: **{c_name_val}**")
        
        e_name = st.text_input("Onomatepwnymo", value=str(c_row_data.get('CuName', c_row_data.get('Name', ''))), key=f"ec_name_{c_name_val}")
        e_mobile1 = st.text_input("Kinito-1", value=str(c_row_data.get('CuPhone', '')), key=f"ec_mob1_{c_name_val}")
        e_mobile2 = st.text_input("Kinito-2", value=str(c_row_data.get('CuMobile', '')), key=f"ec_mob2_{c_name_val}")
        e_address = st.text_input("Dieythynsi", value=str(c_row_data.get('CuAddress', '')), key=f"ec_addr_{c_name_val}")
        e_city = st.text_input("Poli", value=str(c_row_data.get('CuCity', '')), key=f"ec_city_{c_name_val}")
        e_email = st.text_input("Email", value=str(c_row_data.get('CuEmail', '')), key=f"ec_email_{c_name_val}")
        e_notes = st.text_area("Simeioseis", value=str(c_row_data.get('CuNotes', '')), key=f"ec_notes_{c_name_val}")
        
        if save_clicked:
            try:
                cell = ws_customers.find(c_name_val)
                ws_customers.update_cell(cell.row, df_customers.columns.get_loc(name_col) + 1, e_name)
                ws_customers.update_cell(cell.row, 5, e_mobile1)
                ws_customers.update_cell(cell.row, 6, e_mobile2)
                ws_customers.update_cell(cell.row, 3, e_address)
                ws_customers.update_cell(cell.row, 4, e_city)
                ws_customers.update_cell(cell.row, 7, e_email)
                ws_customers.update_cell(cell.row, 8, e_notes)
                
                st.cache_data.clear()
                st.session_state['active_subview'] = 'menu'
                st.rerun()
            except Exception as e:
                st.error(f"❌ Sfalma: {e}")

# ---------------------------------------------------------
# 3. NEO EIDOS KATALOGOY
# ---------------------------------------------------------
def render_new_item_tab(df_items, get_worksheet):
    ws_items = get_worksheet("Items")

    with st.form("new_item_form", clear_on_submit=True):
        col_nav, col_empty, col_save = st.columns([1, 1, 1])
        
        with col_nav:
            if st.form_submit_button("🏠 ARXIKI", use_container_width=True):
                st.session_state['active_subview'] = 'menu'
                st.rerun()

        with col_save:
            submitted = st.form_submit_button("💾 APO8IKEYSI", type="primary", use_container_width=True)

        st.markdown("### ➕ Neo Eidos Katalogoy")
        
        it_name = st.text_input("Onoma Eidous (p.x. Mpourfan)")
        it_desc = st.selectbox("Perigrafi / Katigoria", ["Rouxa", "Xalia"])
        it_price = st.number_input("TIMI (€)", min_value=0.0, step=0.5)
        it_price_m2 = st.number_input("TIMI TETRAGWNIKOY (€/m²)", min_value=0.0, step=0.5)
        
        if submitted:
            if not it_name:
                st.error("Valte onoma eidous.")
            else:
                all_vals = ws_items.get_all_records()
                df_fresh = pd.DataFrame(all_vals)
                
                item_id = 1 if df_fresh.empty or 'ItemID' not in df_fresh.columns else int(pd.to_numeric(df_fresh['ItemID'], errors='coerce').max() or 0) + 1
                ws_items.append_row([item_id, it_name, it_desc, it_price, it_price_m2])
                
                st.cache_data.clear()
                st.session_state['active_subview'] = 'menu'
                st.rerun()

# ---------------------------------------------------------
# 4. TROPOPOISI KATALOGOY (Diavazei AMESA freska dedomena)
# ---------------------------------------------------------
def render_edit_item_tab(df_items_old, get_worksheet):
    st.markdown("### ✏️ Tropopoiisi Katalogoy")
    ws_items = get_worksheet("Items")

    col_nav, col_save = st.columns([1, 1])
    with col_nav:
        if st.button("🏠 ARXIKI", key="btn_home_edit_item", use_container_width=True):
            st.session_state['active_subview'] = 'menu'
            st.rerun()
    with col_save:
        save_clicked_item = st.button("💾 APO8IKEYSI", key="btn_save_edit_item", type="primary", use_container_width=True)

    st.markdown("<hr style='margin: 8px 0px;'>", unsafe_allow_html=True)

    # DIAVAZOYME FRESTKA DEDOMENA APO TO GOOGLE SHEET APEUTHEIAS!
    data = ws_items.get_all_records()
    df_items = pd.DataFrame(data)

    col_name_key = 'ItName' if 'ItName' in df_items.columns else ('Name' if 'Name' in df_items.columns else None)
    col_desc_key = 'Category' if 'Category' in df_items.columns else ('Description' if 'Description' in df_items.columns else None)

    if df_items.empty or not col_name_key:
        st.info("Den yparxoun apothikeymena eidi.")
        return

    valid_items = df_items[df_items[col_name_key].astype(str).str.strip() != ""]
    
    item_options = ["-- Epilexte eidos --"]
    item_map = {}
    for _, r in valid_items.iterrows():
        name_val = str(r[col_name_key]).strip()
        cat_val = str(r[col_desc_key]).strip() if col_desc_key and pd.notnull(r[col_desc_key]) else "Rouxa"
        display_str = f"{name_val} ({cat_val})"
        item_options.append(display_str)
        item_map[display_str] = name_val

    selected_display = st.selectbox("Anazitisi Eidous", item_options, label_visibility="collapsed", key="search_item_selectbox_top")

    if selected_display and selected_display != "-- Epilexte eidos --":
        real_name = item_map[selected_display]
        row_data = valid_items[valid_items[col_name_key].astype(str).str.strip() == real_name].iloc[0]
        curr_price = float(row_data.get('Price', 0.0) or 0.0) if 'Price' in df_items.columns else 0.0
        curr_price_m2 = float(row_data.get('Price m2', row_data.get('Price_m2', 0.0)) or 0.0)
        curr_cat = str(row_data.get(col_desc_key, "Rouxa")) if col_desc_key else "Rouxa"

        st.markdown(f"✏️ Epexergasia: **{real_name}**")
        
        new_it_name = st.text_input("Onoma Eidous", value=real_name, key=f"ei_name_{real_name}")
        
        cat_index = 0 if curr_cat.strip().lower() == "rouxa" else 1 if curr_cat.strip().lower() == "xalia" else 0
        new_cat = st.selectbox("Perigrafi / Katigoria", ["Rouxa", "Xalia"], index=cat_index, key=f"ei_cat_{real_name}")
        
        new_price = st.number_input("TIMI (€)", value=curr_price, min_value=0.0, step=0.5, key=f"ei_price_{real_name}")
        new_price_m2 = st.number_input("TIMI TETRAGWNIKOY (€/m²)", value=curr_price_m2, min_value=0.0, step=0.5, key=f"ei_pricem2_{real_name}")
        
        if save_clicked_item:
            try:
                cell = ws_items.find(real_name)
                ws_items.update_cell(cell.row, 2, new_it_name)
                if col_desc_key:
                    ws_items.update_cell(cell.row, df_items.columns.get_loc(col_desc_key) + 1, new_cat)
                ws_items.update_cell(cell.row, 3, new_price)
                ws_items.update_cell(cell.row, 4, new_price_m2)
                
                st.cache_data.clear()
                st.session_state['active_subview'] = 'menu'
                st.rerun()
            except Exception as e:
                st.error(f"❌ Sfalma: {e}")
