import streamlit as st
import pandas as pd
from datetime import datetime

STATUS_OPTIONS = ["Πλύσιμο", "Φύλαξη", "Πλύσιμο & Φύλαξη", "Έτοιμο", "Παραδόθηκε"]

# --- ENIAIO CSS STYLING XΩΡΙΣ ΜΠΛΕ ΠΛΑΙΣΙΑ ΣΤΙΣ ΣΤΗΛΕΣ ---
st.markdown("""
    <style>
        /* Στυλ για το κουμπί ΑΡΧΙΚΗ ώστε να είναι καθαρό χωρίς γύρω-γύρω */
        .home-btn-container .stButton > button {
            background-color: #36456b !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: 500 !important;
            height: 42px !important;
            width: 200px !important; /* Σταθερό κομψό πλάτος */
        }
        .home-btn-container .stButton > button:hover {
            background-color: #28334f !important;
        }
        div[data-testid="stVerticalBlock"] > div {
            gap: 0.4rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- 1. ΤΡΟΠΟΠΟΙΗΣΗ ΧΑΛΙΩΝ (TrXalia) ---
def render_edit_xalia_tab(df_xalia, df_customers, df_items, get_worksheet_fn):
    # Καθαρό κουμπί χωρίς st.columns για να μην παίρνει το γύρω-γύρω μπλε πλαίσιο
    st.markdown('<div class="home-btn-container">', unsafe_allow_html=True)
    if st.button("🏠 ΑΡΧΙΚΗ", key="back_home_xalia"):
        st.session_state['active_subview'] = 'menu'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 🔍 Αναζήτηση & Τροποποίηση Χαλιών (TrXalia)")
    
    if df_xalia.empty:
        st.info("Δεν βρέθηκαν εγγραφές στα Χαλιά.")
        return

    df_active = df_xalia[df_xalia['Status'] != 'Παραδόθηκε'].copy()
    
    if not df_items.empty:
        df_items.columns = df_items.columns.str.strip()
        col_name_key = next((ik for ik in ['ItName', 'Name', 'ItemName'] if ik in df_items.columns), None)
        col_cat_key = next((ck for ck in ['Category', 'CAT', 'CategoryName'] if ck in df_items.columns), None)
        
        if col_name_key and col_cat_key:
            xalia_items_list = df_items[
                df_items[col_cat_key].astype(str).str.strip().str.lower() == "χαλιά"
            ][col_name_key].dropna().astype(str).str.strip().tolist()
            
            if xalia_items_list:
                df_active = df_active[
                    df_active['ItName'].astype(str).str.strip().isin(xalia_items_list)
                ]

    if df_active.empty:
        st.success("🎉 Δεν υπάρχουν εκκρεμότητες στα χαλιά!")
        return

    search_query = st.text_input("🔎 Αναζήτηση με Όνομα Πελάτη, Κινητό/Τηλέφωνο ή Barcode:", key="search_xalia_input")

    cust_phone_map = {}
    if not df_customers.empty:
        df_cust_copy = df_customers.copy()
        df_cust_copy.columns = df_cust_copy.columns.str.strip()
        c_name_col = next((c for c in ['CuName', 'Name', 'CustomerName'] if c in df_cust_copy.columns), None)
        
        if c_name_col:
            for _, c_row in df_cust_copy.iterrows():
                cust_name = str(c_row[c_name_col]).strip()
                phones = []
                for p_col in ['CuMobile', 'CuPhone', 'Mobile', 'Phone', 'TEL', 'Τηλέφωνο']:
                    if p_col in df_cust_copy.columns and pd.notnull(c_row[p_col]):
                        clean_p = str(c_row[p_col]).replace(" ", "").replace("-", "").replace("+", "").replace("(", "").replace(")", "").strip()
                        if clean_p:
                            phones.append(clean_p)
                cust_phone_map[cust_name] = " ".join(phones)

    if search_query:
        q_raw = search_query.strip().lower()
        q_clean_num = q_raw.replace(" ", "").replace("-", "").replace("+", "").replace("(", "").replace(")", "")

        def match_row(row):
            c_name = str(row.get('CustomerName', '')).strip().lower()
            code_val = str(row.get('Code', '')).strip().lower()
            phone_val = cust_phone_map.get(str(row.get('CustomerName', '')).strip(), '').lower()
            return (q_raw in c_name) or (q_raw in code_val) or ((q_clean_num in phone_val) if q_clean_num else False)

        df_filtered = df_active[df_active.apply(match_row, axis=1)]
    else:
        df_filtered = df_active

    if df_filtered.empty:
        st.warning("⚠️ Δεν βρέθηκαν ενεργές εγγραφές.")
        return

    st.write(f"Βρέθηκαν **{len(df_filtered)}** ενεργές εγγραφές:")
    ws = get_worksheet_fn("TrXalia")

    for idx, row in df_filtered.iterrows():
        tr_id = str(row['TransactionID'])
        c_name = row.get('CustomerName', 'Άγνωστος')
        code_val = str(row.get('Code', '-'))
        place_val = row.get('Place', row.get('Shelf', '-'))
        status_val = row.get('Status', '-')
        item_name = row.get('ItName', '')
        phone_show = cust_phone_map.get(c_name, '-')
        
        try:
            price_val = float(row.get('TotalPrice', 0.0))
        except:
            price_val = 0.0

        is_etoimo = (status_val == "Έτοιμο")
        prefix_icon = "🟢 [ΕΤΟΙΜΟ] " if is_etoimo else "📌 "
        expander_label = f"{prefix_icon}ID: #{tr_id} | {c_name} ({phone_show}) | Barcode: {code_val} | Θέση: {place_val} | Τιμή: {price_val}€ | Κατάσταση: {status_val} | {item_name}"

        with st.expander(expander_label):
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                new_len = st.text_input("Μήκος (m)", value=str(row.get('Length', '')), key=f"len_{tr_id}_{idx}")
            with col2:
                new_hei = st.text_input("Ύψος (m)", value=str(row.get('Height', '')), key=f"hei_{tr_id}_{idx}")
            with col3:
                new_place = st.text_input("Θέση", value=str(place_val), key=f"plc_{tr_id}_{idx}")
            with col4:
                new_price = st.number_input("Τιμή (€)", value=price_val, step=1.0, key=f"prc_{tr_id}_{idx}")
            with col5:
                curr_st = row.get('Status', STATUS_OPTIONS[0])
                new_st = st.selectbox(
                    "Κατάσταση", STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(curr_st) if curr_st in STATUS_OPTIONS else 0,
                    key=f"st_x_{tr_id}_{idx}"
                )

            if st.button("💾 Αποθήκευση Αλλαγών", key=f"btn_save_x_{tr_id}_{idx}", type="primary", use_container_width=True):
                try:
                    id_col = ws.col_values(1)
                    sheet_row = id_col.index(tr_id) + 1 if tr_id in id_col else idx + 2
                    cols = df_xalia.columns.tolist()

                    if "Length" in cols: ws.update_cell(sheet_row, cols.index("Length") + 1, new_len)
                    if "Height" in cols: ws.update_cell(sheet_row, cols.index("Height") + 1, new_hei)
                    
                    place_col_name = "Place" if "Place" in cols else ("Shelf" if "Shelf" in cols else None)
                    if place_col_name: ws.update_cell(sheet_row, cols.index(place_col_name) + 1, new_place)
                    if "TotalPrice" in cols: ws.update_cell(sheet_row, cols.index("TotalPrice") + 1, new_price)
                    if "Status" in cols:
                        ws.update_cell(sheet_row, cols.index("Status") + 1, new_st)
                        if new_st == "Παραδόθηκε" and "DateOut" in cols:
                            ws.update_cell(sheet_row, cols.index("DateOut") + 1, datetime.now().strftime("%Y-%m-%d %H:%M"))

                    st.session_state['df_tr_xalia'] = pd.DataFrame(ws.get_all_records())
                    st.success("✅ Επιτυχής ενημέρωση!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Σφάλμα: {e}")


# --- 2. ΤΡΟΠΟΠΟΙΗΣΗ ΡΟΥΧΩΝ / ΕΙΔΩΝ (TrEidi) ---
def render_edit_items_tab(df_items_trans, df_customers, get_worksheet_fn):
    st.markdown('<div class="home-btn-container">', unsafe_allow_html=True)
    if st.button("🏠 ΑΡΧΙΚΗ", key="back_home_items"):
        st.session_state['active_subview'] = 'menu'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 🔍 Αναζήτηση & Τροποποίηση Ρούχων / Ειδών (TrEidi)")
    
    if df_items_trans.empty:
        st.info("Δεν βρέθηκαν εγγραφές στα Ρούχα.")
        return

    df_active = df_items_trans[df_items_trans['Status'] != 'Παραδόθηκε'].copy()
    
    if df_active.empty:
        st.success("🎉 Δεν υπάρχουν εκκρεμότητες στα ρούχα!")
        return

    search_query = st.text_input("🔎 Αναζήτηση με Όνομα Πελάτη ή Τηλέφωνο:", key="search_items_input")

    cust_phone_map = {}
    if not df_customers.empty:
        df_cust_copy = df_customers.copy()
        df_cust_copy.columns = df_cust_copy.columns.str.strip()
        c_name_col = next((c for c in ['CuName', 'Name', 'CustomerName'] if c in df_cust_copy.columns), None)
        
        if c_name_col:
            for _, c_row in df_cust_copy.iterrows():
                cust_name = str(c_row[c_name_col]).strip()
                phones = []
                for p_col in ['CuMobile', 'CuPhone', 'Mobile', 'Phone', 'TEL']:
                    if p_col in df_cust_copy.columns and pd.notnull(c_row[p_col]):
                        clean_p = str(c_row[p_col]).replace(" ", "").replace("-", "").replace("+", "").replace("(", "").replace(")", "").strip()
                        if clean_p: phones.append(clean_p)
                cust_phone_map[cust_name] = " ".join(phones)

    if search_query:
        q_raw = search_query.strip().lower()
        q_clean_num = q_raw.replace(" ", "").replace("-", "").replace("+", "").replace("(", "").replace(")", "")

        def match_row(row):
            c_name = str(row.get('CustomerName', '')).strip().lower()
            phone_val = cust_phone_map.get(str(row.get('CustomerName', '')).strip(), '').lower()
            return (q_raw in c_name) or ((q_clean_num in phone_val) if q_clean_num else False)

        df_filtered = df_active[df_active.apply(match_row, axis=1)]
    else:
        df_filtered = df_active

    if df_filtered.empty:
        st.warning("⚠️ Δεν βρέθηκαν εγγραφές.")
        return

    st.write(f"Βρέθηκαν **{len(df_filtered)}** ενεργές εγγραφές:")
    ws = get_worksheet_fn("TrEidi")

    for idx, row in df_filtered.iterrows():
        tr_id = str(row['TransactionID'])
        c_name = row.get('CustomerName', 'Άγνωστος')
        phone_show = cust_phone_map.get(c_name, '-')
        shelf_val = row.get('Shelf', row.get('Place', '-'))
        status_val = row.get('Status', '-')
        
        try:
            curr_pr = float(row.get('TotalPrice', 0.0))
        except:
            curr_pr = 0.0

        is_etoimo = (status_val == "Έτοιμο")
        prefix_icon = "🟢 [ΕΤΟΙΜΟ] " if is_etoimo else "👕 "
        expander_label = f"{prefix_icon}ID: #{tr_id} | {c_name} ({phone_show}) | Θέση: {shelf_val} | Τιμή: {curr_pr}€ | Κατάσταση: {status_val} | {row.get('ItName', '')}"

        with st.expander(expander_label):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_shelf = st.text_input("Ράφι / Θέση (Shelf)", value=str(shelf_val), key=f"shf_{tr_id}_{idx}")
            with col2:
                new_price = st.number_input("Τιμή (€)", value=curr_pr, step=1.0, key=f"prc_it_{tr_id}_{idx}")
            with col3:
                curr_st = row.get('Status', STATUS_OPTIONS[0])
                new_st = st.selectbox(
                    "Κατάσταση", STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(curr_st) if curr_st in STATUS_OPTIONS else 0,
                    key=f"st_it_{tr_id}_{idx}"
                )

            if st.button("💾 Αποθήκευση Αλλαγών", key=f"btn_save_it_{tr_id}_{idx}", type="primary", use_container_width=True):
                try:
                    id_col = ws.col_values(1)
                    sheet_row = id_col.index(tr_id) + 1 if tr_id in id_col else idx + 2
                    cols = df_items_trans.columns.tolist()
                    shelf_col_name = "Shelf" if "Shelf" in cols else "Place"
                    
                    if shelf_col_name in cols: ws.update_cell(sheet_row, cols.index(shelf_col_name) + 1, new_shelf)
                    if "TotalPrice" in cols: ws.update_cell(sheet_row, cols.index("TotalPrice") + 1, new_price)
                    if "Status" in cols:
                        ws.update_cell(sheet_row, cols.index("Status") + 1, new_st)
                        if new_st == "Παραδόθηκε" and "DateOut" in cols:
                            ws.update_cell(sheet_row, cols.index("DateOut") + 1, datetime.now().strftime("%Y-%m-%d %H:%M"))

                    st.session_state['df_tr_items'] = pd.DataFrame(ws.get_all_records())
                    st.success("✅ Επιτυχής ενημέρωση!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Σφάλμα: {e}")


# --- 3. ΚΑΤΑΧΩΡΗΣΗ ΡΟΥΧΩΝ / ΕΙΔΩΝ ---
def render_item_loading_tab(df_customers, df_items, get_worksheet_fn):
    st.markdown('<div class="home-btn-container">', unsafe_allow_html=True)
    if st.button("🏠 ΑΡΧΙΚΗ", key="back_home_load_item"):
        st.session_state['active_subview'] = 'menu'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 👕 Καταχώρηση Ρούχων & Ειδών")
    
    if df_customers.empty:
        st.warning("⚠️ Δεν βρέθηκαν πελάτες.")
        return

    name_col = 'CuName' if 'CuName' in df_customers.columns else 'Name'
    cust_choices = ["-- Επιλέξτε Πελάτη --"] + df_customers[name_col].dropna().tolist()

    item_name_col = 'ItName' if 'ItName' in df_items.columns else 'Name'
    item_choices = ["-- Επιλέξτε Είδος --"] + (df_items[item_name_col].dropna().tolist() if not df_items.empty else ["Κουστούμι", "Πάπλωμα", "Μπουφάν"])

    with st.form("item_loading_form", clear_on_submit=True):
        sel_cust = st.selectbox("Πελάτης", cust_choices)
        sel_item = st.selectbox("Είδος", item_choices)
        shelf = st.text_input("Ράφι / Θέση")
        price = st.number_input("Τιμή (€)", min_value=0.0, step=0.5)
        status = st.selectbox("Εργασία / Κατάσταση", ["Πλύσιμο", "Στεγνό Καθάρισμα", "Σιδέρωμα"])

        submitted = st.form_submit_button("💾 Αποθήκευση Είδους", type="primary", use_container_width=True)

    if submitted:
        if sel_cust == "-- Επιλέξτε Πελάτη --" or sel_item == "-- Επιλέξτε Είδος --":
            st.error("❌ Παρακαλώ συμπληρώστε Πελάτη και Είδος!")
        else:
            try:
                ws = get_worksheet_fn("TrEidi")
                data = ws.get_all_records()
                df = pd.DataFrame(data)
                
                next_id = 1
                if not df.empty and 'TransactionID' in df.columns:
                    ids = pd.to_numeric(df['TransactionID'], errors='coerce').dropna()
                    if not ids.empty: next_id = int(ids.max()) + 1

                row_data = [
                    next_id, sel_cust, sel_item, shelf,
                    datetime.now().strftime("%Y-%m-%d %H:%M"), "", price, status
                ]
                
                ws.append_row(row_data)
                st.session_state['df_tr_items'] = pd.DataFrame()
                st.success(f"✅ Το είδος καταχωρήθηκε επιτυχώς με μοναδικό ID #{next_id}!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Σφάλμα: {e}")
