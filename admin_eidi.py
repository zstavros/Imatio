import streamlit as st
import pandas as pd
from datetime import datetime

STATUS_OPTIONS = [
    "Έτοιμος για παραλαβή",
    "Προς επεξεργασία",
    "Προς φύλαξη",
    "Παραδόθηκε"
]

def render_admin_eidi_dashboard(load_tab_data, get_worksheet):
    # CSS: Megala grammata MONO stis karteles kai midenismos perithorion
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
        
        div.stTextInput input {
            min-height: 28px !important;
            height: 28px !important;
            padding-top: 1px !important;
            padding-bottom: 1px !important;
            font-size: 0.95rem !important;
        }
        
        div.stTextArea textarea {
            min-height: 85px !important;
            height: 85px !important;
            font-size: 0.95rem !important;
        }
        
        .stForm {
            padding: 2px !important;
            margin-bottom: 0px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    df_customers = load_tab_data("Customers")
    df_items = load_tab_data("Items")
    df_tr_items = load_tab_data("TrItems")
    df_tr_xalia = load_tab_data("TrXalia")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Νέα", 
        "📋 Ανοιχτά", 
        "👥 Πελάτες", 
        "👕 Είδη", 
        "🧺 Χαλιά"
    ])

    # --- 1. ΝΕΑ ΠΑΡΑΔΟΣΗ (Mapeia pollaplon eidwn me data_editor) ---
    with tab1:
        category_type = st.selectbox("Κατηγορία", ["👕 Ρούχα (TrItems)", "🧺 Χαλιά (TrXalia)"], key="new_trans_category")

        name_col = 'CuName' if 'CuName' in df_customers.columns else 'Name'
        if df_customers.empty or name_col not in df_customers.columns:
            st.warning("Πρώτα καταχωρήστε πελάτες στην καρτέλα 'Πελάτες'.")
            st.stop()
        
        cust_choices = ["-- Επιλέξτε Πελάτη --"]
        for _, row in df_customers.iterrows():
            if pd.notnull(row.get(name_col)) and str(row.get(name_col)).strip() != '':
                phone = row.get('CuMobile') if pd.notnull(row.get('CuMobile')) and str(row.get('CuMobile')).strip() != '' else row.get('CuPhone', '')
                cust_choices.append(f"{row[name_col]} ({phone})")

        selected_customer_str = st.selectbox("Επιλογή Πελάτη", cust_choices, key="sel_cust_new")

        col_name_key = 'ItName' if 'ItName' in df_items.columns else 'Name'
        item_choices = df_items[col_name_key].dropna().tolist() if not df_items.empty and col_name_key in df_items.columns else ["Παντελόνι", "Πουκάμισο", "Μπλούζα", "Μπουφάν"]

        st.markdown("<p style='font-size: 0.95rem; font-weight: bold; margin-bottom: 2px;'>Καταχώρηση Ειδών & Θέσεων (Προσθέστε γραμμές +):</p>", unsafe_allow_html=True)

        # Arxikoskenos pinakas gia to data_editor
        if "editor_df" not in st.session_state:
            st.session_state.editor_df = pd.DataFrame(
                [{"Είδος": item_choices[0] if item_choices else "", "Θέση / Ράφι": "", "Κόστος (€)": 0.0}]
            )

        # Data editor gia pollaples grammes
        edited_df = st.data_editor(
            st.session_state.editor_df,
            num_rows="dynamic",
            column_config={
                "Είδος": st.column_config.SelectboxColumn(
                    "Είδος",
                    options=item_choices,
                    required=True
                ),
                "Θέση / Ράφι": st.column_config.TextColumn("Θέση / Ράφι", required=False),
                "Κόστος (€)": st.column_config.NumberColumn("Κόστος (€)", min_value=0.0, step=0.5)
            },
            key="multi_items_editor",
            use_container_width=True
        )

        initial_status = st.selectbox("Αρχική Κατάσταση για όλα", STATUS_OPTIONS, index=1, key="init_status_multi")

        if st.button("💾 Καταχώρηση Όλων των Ειδών", type="primary"):
            if selected_customer_str == "-- Επιλέξτε Πελάτη --":
                st.error("❌ Επιλέξτε πελάτη πρώτα!")
            elif edited_df.empty:
                st.error("❌ Δεν έχετε προσθέσει κανένα είδος!")
            else:
                cust_name_clean = selected_customer_str.split(" (")[0]
                cust_id = int(df_customers[df_customers[name_col] == cust_name_clean]['CustomerID'].values[0])
                today_str = datetime.now().strftime("%Y-%m-%d %H:%M")

                ws_tr = get_worksheet("TrItems" if "Ρούχα" in category_type else "TrXalia")
                current_tr_df = df_tr_items if "Ρούχα" in category_type else df_tr_xalia
                
                next_trans_id = 1 if current_tr_df.empty or 'TransactionID' not in current_tr_df.columns else int(current_tr_df['TransactionID'].max()) + 1

                # Apothikeysi mias-mias grammis ston pinaka tou Google Sheets
                for _, row in edited_df.iterrows():
                    item_name = row.get("Είδος", "")
                    place = row.get("Θέση / Ράφι", "")
                    cost = float(row.get("Κόστος (€)", 0.0))

                    if str(item_name).strip() != "":
                        ws_tr.append_row([next_trans_id, cust_id, item_name, place, today_str, "", cost, initial_status])
                        next_trans_id += 1

                st.success("✅ Όλα τα είδη καταχωρήθηκαν επιτυχώς με τις θέσεις τους!")
                st.cache_data.clear()
                st.rerun()

    # --- 2. ΑΝΟΙΧΤΑ ---
    with tab2:
        sub_tab_c, sub_tab_x = st.tabs(["👕 Ρούχα", "🧺 Χαλιά"])
        with sub_tab_c:
            _render_active_list(df_tr_items, df_customers, "TrItems", get_worksheet)
        with sub_tab_x:
            _render_active_list(df_tr_xalia, df_customers, "TrXalia", get_worksheet)

    # --- 3. ΠΕΛΑΤΕΣ ---
    with tab3:
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

    # --- 4. ΕΙΔΗ ---
    with tab4:
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

    # --- 5. ΧΑΛΙΑ ---
    with tab5:
        st.info("ℹ️ Χρησιμοποιείται η κεντρική βάση ειδών (Items) για καταχώρηση χαλιών.")


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
                ws.update_cell(cell.row, df_trans.columns.get_loc("Status") + 1, new_st)
                if new_st == "Παραδόθηκε":
                    ws.update_cell(cell.row, df_trans.columns.get_loc("DateOut") + 1, datetime.now().strftime("%Y-%m-%d %H:%M"))
                st.toast("Ενημερώθηκε!")
                st.cache_data.clear()
                st.rerun()
