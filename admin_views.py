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
    df_customers = load_tab_data("Customers")
    df_items = load_tab_data("Items")
    df_tr_items = load_tab_data("TrItems")
    df_tr_xalia = load_tab_data("TrXalia")

    # Χρησιμοποιούμε καθαρά st.tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Nea Paradosi", 
        "📋 Anoikta", 
        "👥 Pelates", 
        "👕 Eidi", 
        "🧺 Xalia"
    ])

    # --- 1. NEA PARADOSI ---
    with tab1:
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            st.markdown("### 📝 Nea Paradosi")
        with col2:
            if st.button("🚪 Exodos", key="ex_tab1"):
                st.session_state.admin_logged_in = False
                st.cache_data.clear()
                st.rerun()

        with st.form("new_transaction_form", clear_on_submit=True):
            category_type = st.selectbox("Katigoria", ["👕 Roucha (TrItems)", "🧺 Xalia (TrXalia)"])

            name_col = 'CuName' if 'CuName' in df_customers.columns else 'Name'
            if df_customers.empty or name_col not in df_customers.columns:
                st.warning("Prota katachoriste pelates stin kartela 'Pelates'.")
                st.stop()
            
            cust_choices = []
            for _, row in df_customers.iterrows():
                if pd.notnull(row.get(name_col)) and str(row.get(name_col)).strip() != '':
                    phone = row.get('CuMobile') if pd.notnull(row.get('CuMobile')) and str(row.get('CuMobile')).strip() != '' else row.get('CuPhone', '')
                    cust_choices.append(f"{row[name_col]} ({phone})")

            selected_customer_str = st.selectbox("Epilogi Pelati", cust_choices)

            col_name_key = 'ItName' if 'ItName' in df_items.columns else 'Name'
            if df_items.empty or col_name_key not in df_items.columns:
                item_name_input = st.text_input("Onoma Eidous")
            else:
                item_choices = df_items[col_name_key].dropna().tolist()
                item_name_input = st.selectbox("Epilogi Eidous apo Katachorimena", item_choices)

            place_val = st.text_input("Thesi / Rafi (Place)")
            price = st.number_input("Synoliko Kostos (€)", min_value=0.0, step=0.50)
            initial_status = st.selectbox("Archiki Katastasi", STATUS_OPTIONS, index=1)

            if st.form_submit_button("Katachorisi Neas Paralavis"):
                cust_name_clean = selected_customer_str.split(" (")[0]
                cust_id = int(df_customers[df_customers[name_col] == cust_name_clean]['CustomerID'].values[0])
                today_str = datetime.now().strftime("%Y-%m-%d %H:%M")

                if "Roucha" in category_type:
                    ws_tr = get_worksheet("TrItems")
                    trans_id = 1 if df_tr_items.empty or 'TransactionID' not in df_tr_items.columns else int(df_tr_items['TransactionID'].max()) + 1
                    ws_tr.append_row([trans_id, cust_id, item_name_input, place_val, today_str, "", price, initial_status])
                else:
                    ws_tr = get_worksheet("TrXalia")
                    trans_id = 1 if df_tr_xalia.empty or 'TransactionID' not in df_tr_xalia.columns else int(df_tr_xalia['TransactionID'].max()) + 1
                    ws_tr.append_row([trans_id, cust_id, item_name_input, place_val, today_str, "", price, initial_status])

                st.success("I synallagi katachorithike epitychos!")
                st.cache_data.clear()
                st.rerun()

    # --- 2. ANOIXTA ---
    with tab2:
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            st.markdown("### 📋 Anoikta")
        with col2:
            if st.button("🚪 Exodos", key="ex_tab2"):
                st.session_state.admin_logged_in = False
                st.cache_data.clear()
                st.rerun()

        sub_tab_c, sub_tab_x = st.tabs(["👕 Roucha", "🧺 Xalia"])

        with sub_tab_c:
            _render_active_list(df_tr_items, df_customers, "TrItems", get_worksheet)

        with sub_tab_x:
            _render_active_list(df_tr_xalia, df_customers, "TrXalia", get_worksheet)

    # --- 3. PELATES ---
    with tab3:
        # Ο τίτλος μπαίνει ακριβώς στη γραμμή του Exodos
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            st.markdown("### 👥 Diacheirisi Pelaton")
        with col2:
            if st.button("🚪 Exodos", key="ex_tab3"):
                st.session_state.admin_logged_in = False
                st.cache_data.clear()
                st.rerun()

        customer_mode = st.radio("Epilogi:", ["Neos Pelatis", "Epexergasia Yparchontos"], horizontal=True, key="c_mode_radio")
        ws_customers = get_worksheet("Customers")

        if customer_mode == "Neos Pelatis":
            with st.form("new_customer_form", clear_on_submit=True):
                n_name = st.text_input("Onomateponymo *")
                n_mobile1 = st.text_input("Kinito-1 (CuPhone)")
                n_mobile2 = st.text_input("Kinito-2 (CuMobile)")
                n_address = st.text_input("Diefthynsi (CuAddress)")
                n_email = st.text_input("Email (CuEmail)")
                n_notes = st.text_area("Simeioseis (CuNotes)")
                
                if st.form_submit_button("Apothikeysi Neou Pelati", type="primary"):
                    if not n_name.strip():
                        st.error("Parakalo sympliroste Onoma.")
                    else:
                        cust_id = 1 if df_customers.empty or 'CustomerID' not in df_customers.columns else int(pd.to_numeric(df_customers['CustomerID'], errors='coerce').max() or 0) + 1
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
                        st.success(f"O pelatis **{n_name}** apothikeytike epitychos!")
                        st.cache_data.clear()
                        st.rerun()

        else:
            name_col = 'CuName' if 'CuName' in df_customers.columns else 'Name'
            if df_customers.empty or name_col not in df_customers.columns:
                st.warning("Den vrethikan katachorimenoi pelates.")
            else:
                st.write("Grapste onoma i kinito gia amesi anevresi:")
                search_query = st.text_input("Anazitisi pelati", placeholder="p.x. Stavros i 69...", label_visibility="collapsed")

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
                    st.info("Pliktrologiste merika grammata apo to onoma i to tilefono.")
                elif filtered_df.empty:
                    st.warning("Den vrethike pelatis.")
                else:
                    cust_options = []
                    for _, row in filtered_df.iterrows():
                        phone = row.get('CuPhone') if pd.notnull(row.get('CuPhone')) and str(row.get('CuPhone')).strip() != '' else row.get('CuMobile', '')
                        cust_options.append(f"{row[name_col]} ({phone})")

                    selected_c = st.selectbox("Apotelesmata Anazitisis", cust_options, label_visibility="collapsed")

                    if selected_c:
                        c_name_val = selected_c.split(" (")[0]
                        c_row_data = filtered_df[filtered_df[name_col] == c_name_val].iloc[0]
                        
                        with st.form("edit_customer_form"):
                            st.write(f"Epexergasia pelati: **{c_
