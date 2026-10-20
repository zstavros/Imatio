import streamlit as st
import pandas as pd
from datetime import datetime

STATUS_OPTIONS = ["Πλύσιμο", "Φύλαξη", "Πλύσιμο & Φύλαξη", "Έτοιμο", "Παραδόθηκε"]

# --- 1. ΤΡΟΠΟΠΟΙΗΣΗ ΧΑΛΙΩΝ (TrXalia) ---
def render_edit_xalia_tab(df_xalia, df_customers, df_items, get_worksheet_fn):
    st.markdown("### 🔍 Αναζήτηση & Τροποποίηση Χαλιών (TrXalia)")
    
    if df_xalia.empty:
        st.info("Δεν βρέθηκαν εγγραφές στα Χαλιά.")
        return

    # 1. Εξαιρούμε οριστικά όσες εγγραφές είναι "Παραδόθηκε"
    df_active = df_xalia[df_xalia['Status'] != 'Παραδόθηκε'].copy()
    
    # 2. ΦΙΛΤΡΑΡΙΣΜΑ ΜΕ ΤΗ ΣΤΗΛΗ CATEGORY
    if not df_items.empty:
        df_items.columns = df_items.columns.str.strip()
        
        col_name_key = next((ik for ik in ['ItName', 'Name', 'ItemName'] if ik in df_items.columns), None)
        col_cat_key = next((ck for ck in ['Category', 'CAT', 'CategoryName'] if ck in df_items.columns), None)
        
        if col_name_key and col_cat_key:
            # Βρίσκουμε όλα τα ονόματα ειδών που έχουν Category = "Χαλιά"
            xalia_items_list = df_items[
                df_items[col_cat_key].astype(str).str.strip().str.lower() == "χαλιά"
            ][col_name_key].dropna().astype(str).str.strip().tolist()
            
            if xalia_items_list:
                # Κρατάμε μόνο τις εγγραφές των οποίων το ItName είναι στην κατηγορία Χαλιά
                df_active = df_active[
                    df_active['ItName'].astype(str).str.strip().isin(xalia_items_list)
                ]

    if df_active.empty:
        st.success("🎉 Δεν υπάρχουν εκκρεμότητες στα χαλιά!")
        return

    # Πεδίο Αναζήτησης
    search_query = st.text_input("🔎 Αναζήτηση με Όνομα Πελάτη, Κινητό ή Κωδικό (Code):", key="search_xalia_input")

    # Ετοιμάζουμε τα τηλέφωνα πελατών για τη διασταύρωση αναζήτησης
    cust_phone_map = {}
    if not df_customers.empty:
        c_name_col = 'CuName' if 'CuName' in df_customers.columns else 'Name'
        c_phone_col = 'CuMobile' if 'CuMobile' in df_customers.columns else 'CuPhone'
        if c_name_col in df_customers.columns and c_phone_col in df_customers.columns:
            cust_phone_map = dict(zip(df_customers[c_name_col].astype(str), df_customers[c_phone_col].astype(str)))

    if search_query:
        q = search_query.strip().lower()
        
        def match_row(row):
            c_name = str(row.get('CustomerName', '')).lower()
            code_val = str(row.get('Code', '')).lower()
            phone_val = str(cust_phone_map.get(row.get('CustomerName', ''), '')).lower()
            return (q in c_name) or (q in code_val) or (q in phone_val)

        df_filtered = df_active[df_active.apply(match_row, axis=1)]
    else:
        df_filtered = df_active

    if df_filtered.empty:
        st.warning("⚠️ Δεν βρέθηκαν ενεργές εγγραφές με τα κριτήρια που δώσατε.")
        return

    st.write(f"Βρέθηκαν **{len(df_filtered)}** ενεργές εγγραφές:")
    ws = get_worksheet_fn("TrXalia")

        # Εμφάνιση εγγραφών με προσθήκη Θέσης και Κατάστασης στον τίτλο
    for idx, row in df_filtered.iterrows():
        tr_id = str(row['TransactionID'])
        c_name = row.get('CustomerName', 'Άγνωστος')
        code_val = row.get('Code', '-')
        place_val = row.get('Place', row.get('Shelf', '-'))  # Παίρνει τη θέση/ράφι
        status_val = row.get('Status', '-')                  # Παίρνει την κατάσταση
        item_name = row.get('ItName', '')
        phone_show = cust_phone_map.get(c_name, '-')


        expander_label = f"📌 ID: #{tr_id} | Πελάτης: {c_name} ({phone_show}) | Κωδικός: {code_val} | Θέση: {place_val} | Κατάσταση: {status_val} | {item_name}"
        with st.expander(expander_label):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                new_len = st.text_input("Μήκος (m)", value=str(row.get('Length', '')), key=f"len_{tr_id}_{idx}")
            with col2:
                new_hei = st.text_input("Ύψος (m)", value=str(row.get('Height', '')), key=f"hei_{tr_id}_{idx}")
            with col3:
                try:
                    curr_pr = float(row.get('TotalPrice', 0.0))
                except:
                    curr_pr = 0.0
                new_price = st.number_input("Τιμή (€)", value=curr_pr, step=1.0, key=f"prc_{tr_id}_{idx}")
            with col4:
                curr_st = row.get('Status', STATUS_OPTIONS[0])
                new_st = st.selectbox(
                    "Κατάσταση", STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(curr_st) if curr_st in STATUS_OPTIONS else 0,
                    key=f"st_x_{tr_id}_{idx}"
                )

            if st.button("💾 Αποθήκευση Αλλαγών", key=f"btn_save_x_{tr_id}_{idx}", type="primary"):
                try:
                    id_col = ws.col_values(1)
                    if tr_id in id_col:
                        sheet_row = id_col.index(tr_id) + 1
                    else:
                        sheet_row = idx + 2

                    cols = df_xalia.columns.tolist()
                    if "Length" in cols:
                        ws.update_cell(sheet_row, cols.index("Length") + 1, new_len)
                    if "Height" in cols:
                        ws.update_cell(sheet_row, cols.index("Height") + 1, new_hei)
                    if "TotalPrice" in cols:
                        ws.update_cell(sheet_row, cols.index("TotalPrice") + 1, new_price)
                    if "Status" in cols:
                        ws.update_cell(sheet_row, cols.index("Status") + 1, new_st)
                        if new_st == "Παραδόθηκε" and "DateOut" in cols:
                            ws.update_cell(sheet_row, cols.index("DateOut") + 1, datetime.now().strftime("%Y-%m-%d %H:%M"))

                    st.session_state['df_tr_xalia'] = pd.DataFrame()
                    st.success("✅ Η ενημέρωση έγινε επιτυχώς!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Σφάλμα αποθήκευσης: {e}")


# --- 2. ΤΡΟΠΟΠΟΙΗΣΗ ΡΟΥΧΩΝ / ΕΙΔΩΝ (TrEidi) ---
def render_edit_items_tab(df_items_trans, df_customers, get_worksheet_fn):
    st.markdown("### 🔍 Αναζήτηση & Τροποποίηση Ρούχων / Ειδών (TrEidi)")
    
    if df_items_trans.empty:
        st.info("Δεν βρέθηκαν εγγραφές στα Ρούχα.")
        return

    df_active = df_items_trans[df_items_trans['Status'] != 'Παραδόθηκε'].copy()
    
    if df_active.empty:
        st.success("🎉 Δεν υπάρχουν εκκρεμότητες στα ρούχα!")
        return

    search_query = st.text_input("🔎 Αναζήτηση με Όνομα Πελάτη ή Κινητό:", key="search_items_input")

    cust_phone_map = {}
    if not df_customers.empty:
        c_name_col = 'CuName' if 'CuName' in df_customers.columns else 'Name'
        c_phone_col = 'CuMobile' if 'CuMobile' in df_customers.columns else 'CuPhone'
        if c_name_col in df_customers.columns and c_phone_col in df_customers.columns:
            cust_phone_map = dict(zip(df_customers[c_name_col].astype(str), df_customers[c_phone_col].astype(str)))

    if search_query:
        q = search_query.strip().lower()
        def match_row(row):
            c_name = str(row.get('CustomerName', '')).lower()
            phone_val = str(cust_phone_map.get(row.get('CustomerName', ''), '')).lower()
            return (q in c_name) or (q in phone_val)

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

        with st.expander(f"👕 ID: #{tr_id} | Πελάτης: {c_name} ({phone_show}) | Είδος: {row.get('ItName', '')}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_shelf = st.text_input("Ράφι / Θέση (Shelf)", value=str(row.get('Shelf', row.get('Place', ''))), key=f"shf_{tr_id}_{idx}")
            with col2:
                try:
                    curr_pr = float(row.get('TotalPrice', 0.0))
                except:
                    curr_pr = 0.0
                new_price = st.number_input("Τιμή (€)", value=curr_pr, step=1.0, key=f"prc_it_{tr_id}_{idx}")
            with col3:
                curr_st = row.get('Status', STATUS_OPTIONS[0])
                new_st = st.selectbox(
                    "Κατάσταση", STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(curr_st) if curr_st in STATUS_OPTIONS else 0,
                    key=f"st_it_{tr_id}_{idx}"
                )

            if st.button("💾 Αποθήκευση Αλλαγών", key=f"btn_save_it_{tr_id}_{idx}", type="primary"):
                try:
                    id_col = ws.col_values(1)
                    if tr_id in id_col:
                        sheet_row = id_col.index(tr_id) + 1
                    else:
                        sheet_row = idx + 2

                    cols = df_items_trans.columns.tolist()
                    shelf_col_name = "Shelf" if "Shelf" in cols else "Place"
                    
                    if shelf_col_name in cols:
                        ws.update_cell(sheet_row, cols.index(shelf_col_name) + 1, new_shelf)
                    if "TotalPrice" in cols:
                        ws.update_cell(sheet_row, cols.index("TotalPrice") + 1, new_price)
                    if "Status" in cols:
                        ws.update_cell(sheet_row, cols.index("Status") + 1, new_st)
                        if new_st == "Παραδόθηκε" and "DateOut" in cols:
                            ws.update_cell(sheet_row, cols.index("DateOut") + 1, datetime.now().strftime("%Y-%m-%d %H:%M"))

                    st.session_state['df_tr_items'] = pd.DataFrame()
                    st.success("✅ Η ενημέρωση έγινε επιτυχώς!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Σφάλμα αποθήκευσης: {e}")


# --- 3. ΚΑΤΑΧΩΡΗΣΗ ΡΟΥΧΩΝ / ΕΙΔΩΝ ---
def render_item_loading_tab(df_customers, df_items, get_worksheet_fn):
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

        submitted = st.form_submit_button("💾 Αποθήκευση Είδους", type="primary")

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
                    if not ids.empty:
                        next_id = int(ids.max()) + 1

                row_data = [
                    next_id, sel_cust, sel_item, shelf,
                    datetime.now().strftime("%Y-%m-%d %H:%M"), "", price, status
                ]
                
                ws.append_row(row_data)
                st.session_state['df_tr_items'] = pd.DataFrame()
                st.success("✅ Το είδος καταχωρήθηκε επιτυχώς!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Σφάλμα: {e}")
