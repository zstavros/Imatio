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
    # CSS για να ανέβουν όλα ψηλά και να κολλήσουν μεταξύ τους
    st.markdown("""
        <style>
        /* Μείωση κενών στην κορυφή */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
        }
        /* Μικρότερα περιθώρια στους τίτλους */
        h3 {
            margin-top: 0rem !important;
            margin-bottom: 0.2rem !important;
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
        }
        /* Μάζεμα των tabs προς τα πάνω */
        div[data-testid="stTabs"] {
            margin-top: -0.5rem !important;
        }
        div[data-testid="stTabs"] button {
            padding-top: 4px !important;
            padding-bottom: 4px !important;
        }
        /* Μικρότερα ύψη στα πεδία */
        div.stTextInput input {
            min-height: 32px !important;
            height: 32px !important;
            padding-top: 2px !important;
            padding-bottom: 2px !important;
        }
        div.stTextArea textarea {
            min-height: 60px !important;
            height: 60px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Αρχικοποίηση ενεργής καρτέλας για δυναμικό τίτλο
    if "active_tab_title" not in st.session_state:
        st.session_state.active_tab_title = "📝 Nea Paradosi"

    # Πάνω γραμμή: Δυναμικός τίτλος & Κουμπί Έξοδος στην ίδια ευθεία
    col1, col2 = st.columns([0.75, 0.25])
    with col1:
        st.markdown(f"### {st.session_state.active_tab_title}")
    with col2:
        if st.button("🚪 Exodos", key="admin_logout_btn"):
            st.session_state.admin_logged_in = False
            st.cache_data.clear()
            st.rerun()

    df_customers = load_tab_data("Customers")
    df_items = load_tab_data("Items")
    df_tr_items = load_tab_data("TrItems")
    df_tr_xalia = load_tab_data("TrXalia")

    # Καθαρά st.tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Nea Paradosi", 
        "📋 Anoikta", 
        "👥 Pelates", 
        "👕 Eidi", 
        "🧺 Xalia"
    ])

    # --- 1. NEA PARADOSI ---
    with tab1:
        st.session_state.active_tab_title = "📝 Nea Paradosi"
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
        st.session_state.active_tab_title = "📋 Anoikta"
        sub_tab_c, sub_tab_x = st.tabs(["👕 Roucha", "🧺 Xalia"])

        with sub_tab_c:
            _render_active_list(df_tr_items, df_customers, "TrItems", get_worksheet)

        with sub_tab_x:
            _render_active_list(df_tr_xalia, df_customers, "TrXalia", get_worksheet)

    # --- 3. PELATES ---
    with tab3:
        st.session_state.active_tab_title = "👥 Diacheirisi Pelaton"
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
                            st.write(f"Epexergasia pelati: **{c_name_val}**")
                            e_name = st.text_input("Onomateponymo", value=str(c_row_data.get('CuName', c_row_data.get('Name', ''))))
                            e_mobile1 = st.text_input("Kinito-1", value=str(c_row_data.get('CuPhone', '')))
                            e_mobile2 = st.text_input("Kinito-2", value=str(c_row_data.get('CuMobile', '')))
                            e_address = st.text_input("Diefthynsi", value=str(c_row_data.get('CuAddress', '')))
                            e_email = st.text_input("Email", value=str(c_row_data.get('CuEmail', '')))
                            e_notes = st.text_area("Simeioseis", value=str(c_row_data.get('CuNotes', '')))
                            
                            if st.form_submit_button("Enimerosi Stoicheion"):
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
                                    
                                    st.success("Ta stoicheia enimerothikan epitychos!")
                                    st.cache_data.clear()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Sfalma: {e}")

    # --- 4. EIDI ---
    with tab4:
        st.session_state.active_tab_title = "👕 Eidi"
        item_mode = st.radio("Epilogi:", ["Neo Eidos", "Epexergasia"], horizontal=True, key="i_mode")
        ws_items = get_worksheet("Items")

        if item_mode == "Neo Eidos":
            with st.form("new_item_form", clear_on_submit=True):
                it_name = st.text_input("Onoma Eidous (p.x. Mpoufan, Kostoumi)")
                it_desc = st.text_input("Perigrafi / Katigoria")
                if st.form_submit_button("Pros8iki Eidous"):
                    if not it_name:
                        st.error("Valte onoma eidous.")
                    else:
                        item_id = 1 if df_items.empty or 'ItemID' not in df_items.columns else int(df_items['ItemID'].max()) + 1
                        ws_items.append_row([item_id, it_name, it_desc])
                        st.success("To eidos prostetheike!")
                        st.cache_data.clear()
                        st.rerun()
        else:
            col_name_key = 'ItName' if 'ItName' in df_items.columns else 'Name'
            if df_items.empty or col_name_key not in df_items.columns:
                st.info("Den yparchoun apothikeymena eidi.")
            else:
                item_list = df_items[col_name_key].dropna().tolist()
                selected_it = st.selectbox("Epilexte Eidos", item_list)
                if selected_it:
                    with st.form("edit_item_form"):
                        new_it_name = st.text_input("Onoma Eidous", value=selected_it)
                        if st.form_submit_button("Apothikeysi Allagon"):
                            cell = ws_items.find(selected_it)
                            col_idx = df_items.columns.get_loc(col_name_key) + 1
                            ws_items.update_cell(cell.row, col_idx, new_it_name)
                            st.success("Enimerothike!")
                            st.cache_data.clear()
                            st.rerun()

    # --- 5. XALIA ---
    with tab5:
        st.session_state.active_tab_title = "🧺 Xalia"
        st.info("Xrisimopoieitai i kentriki vasi eidon (Items) gia katachorisi chalion.")


def _render_active_list(df_trans, df_cust, sheet_name, get_worksheet_fn):
    if df_trans.empty or 'Status' not in df_trans.columns:
        st.info("Den yparchoun eggrafes.")
        return

    active_data = df_trans[df_trans['Status'] != 'Paradothike']
    if active_data.empty:
        st.info("Den yparchoun ekkremotites.")
        return

    ws = get_worksheet_fn(sheet_name)
    name_col = 'CuName' if 'CuName' in df_cust.columns else 'Name'

    for _, row in active_data.iterrows():
        cust_info = df_cust[df_cust['CustomerID'] == row['CustomerID']]
        c_name = cust_info[name_col].values[0] if not cust_info.empty else "Agnostos"

        with st.expander(f"#{int(row['TransactionID'])} - {c_name} | {row.get('ItName', '')}"):
            st.write(f"Thesi: {row.get('Place', '-')}")
            st.write(f"Kostos: {row.get('TotalPrice', 0)}€")

            curr_st = row.get('Status', 'Pros epexergasia')
            new_st = st.selectbox(
                "Allagi Katastasis", STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(curr_st) if curr_st in STATUS_OPTIONS else 1,
                key=f"st_{sheet_name}_{row['TransactionID']}"
            )
            if new_st != curr_st:
                cell = ws.find(str(row['TransactionID']))
                status_col_idx = df_trans.columns.get_loc("Status") + 1
                ws.update_cell(cell.row, status_col_idx, new_st)
                if new_st == "Paradothike":
                    date_out_idx = df_trans.columns.get_loc("DateOut") + 1
                    ws.update_cell(cell.row, date_out_idx, datetime.now().strftime("%Y-%m-%d %H:%M"))
                st.toast("Enimerothike!")
                st.cache_data.clear()
                st.rerun()
