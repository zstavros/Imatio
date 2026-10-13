import streamlit as st
import pandas as pd
from datetime import datetime

# Οι νέες ακριβείς καταστάσεις που ζητήσατε
STATUS_OPTIONS = [
    "Προς φύλαξη (φορτηγό)",
    "Προς πλύσιμο (φορτηγό)",
    "Πλύσιμο",
    "Σε φύλαξη",
    "Έτοιμο",
    "Παραδόθηκε"
]

def render_new_transaction_tab(df_customers, df_items, df_tr_items, df_tr_xalia, get_worksheet):
    st.subheader("📝 Νέα Καταχώρηση")
    
    # Επιλογή τύπου εργασίας / παραλαβής
    job_type = st.radio(
        "Επιλέξτε Τύπο Εργασίας:",
        ["🚛 Φόρτωση επί αυτοκινήτου (Χαλιά)", "🏪 Παραλαβή στο μαγαζί (Ρούχα)"],
        horizontal=True,
        key="job_type_selector"
    )
    st.divider()

    # 1. Επιλογή Πελάτη
    name_col = 'CuName' if 'CuName' in df_customers.columns else 'Name'
    if df_customers.empty or name_col not in df_customers.columns:
        st.warning("⚠️ Δεν βρέθηκαν πελάτες. Καταχωρήστε πρώτα πελάτες από την καρτέλα 'Πελάτες'.")
        return
    
    cust_choices = ["-- Επιλέξτε Πελάτη --"]
    for _, row in df_customers.iterrows():
        if pd.notnull(row.get(name_col)) and str(row.get(name_col)).strip() != '':
            phone = row.get('CuMobile') if pd.notnull(row.get('CuMobile')) and str(row.get('CuMobile')).strip() != '' else row.get('CuPhone', '')
            cust_choices.append(f"{row[name_col]} ({phone})")

    selected_customer_str = st.selectbox("👤 Επιλογή Πελάτη", cust_choices, key="sel_cust_entry")

    # =========================================================
    # 🚛 ΕΡΓΑΣΙΑ 1: ΦΟΡΤΩΣΗ ΕΠΙ ΑΥΤΟΚΙΝΗΤΟΥ (ΧΑΛΙΑ -> TrXalia)
    # =========================================================
    if "Φόρτωση" in job_type:
        st.markdown("##### 🚛 Στοιχεία Χαλιού (Φόρτωση)")
        
        col_name_key = 'ItName' if 'ItName' in df_items.columns else 'Name'
        raw_items = df_items[col_name_key].dropna().tolist() if not df_items.empty and col_name_key in df_items.columns else ["Χαλί Μηχανής", "Χαλί Χειροποίητο"]
        selected_item = st.selectbox("🏷️ Είδος Χαλιού", ["-- Επιλέξτε Είδος --"] + raw_items, key="truck_item")

        default_price_m2 = 0.0
        if selected_item != "-- Επιλέξτε Είδος --" and not df_items.empty:
            matched_item = df_items[df_items[col_name_key] == selected_item]
            if not matched_item.empty and 'Price m2' in matched_item.columns:
                default_price_m2 = float(matched_item['Price m2'].values[0] or 0.0)

        col1, col2, col3 = st.columns(3)
        with col1:
            length = st.number_input("📏 Μήκος (m)", min_value=0.0, step=0.10, value=0.0, key="carpet_len")
        with col2:
            height = st.number_input("📐 Ύψος (m)", min_value=0.0, step=0.10, value=0.0, key="carpet_hgt")
        with col3:
            sqm = round(length * height, 2)
            st.number_input("🔳 Τετραγωνικά (m²)", value=sqm, disabled=True, key="carpet_sqm")

        col4, col5 = st.columns(2)
        with col4:
            price_m2 = st.number_input("💶 Τιμή Τετραγωνικού (€/m²)", min_value=0.0, step=0.5, value=default_price_m2, key="carpet_pm2")
        with col5:
            total_price = round(sqm * price_m2, 2)
            st.number_input("💰 Τελική Τιμή (€)", value=total_price, disabled=True, key="carpet_total")

        col6, col7 = st.columns(2)
        with col6:
            shelf = st.text_input("📍 Ράφι / Θέση", value="Αποθήκη (Φορτηγό)", key="carpet_shelf")
        with col7:
            status = st.selectbox("🔄 Κατάσταση", STATUS_OPTIONS, index=1, key="carpet_status")

        if st.button("💾 Καταχώρηση Χαλιού στο Φορτηγό", type="primary"):
            if selected_customer_str == "-- Επιλέξτε Πελάτη --":
                st.error("❌ Επιλέξτε πελάτη!")
            elif selected_item == "-- Επιλέξτε Είδος --":
                st.error("❌ Επιλέξτε είδος χαλιού!")
            else:
                cust_name_clean = selected_customer_str.split(" (")[0]
                today_str = datetime.now().strftime("%Y-%m-%d %H:%M")

                ws_trxalia = get_worksheet("TrXalia")
                next_id = 1 if df_tr_xalia.empty or 'TransactionID' not in df_tr_xalia.columns else int(df_tr_xalia['TransactionID'].max()) + 1

                ws_trxalia.append_row([
                    next_id, cust_name_clean, selected_item, length, height, sqm, price_m2, shelf, today_str, "", total_price, status
                ])
                st.success(f"✅ Το χαλί για τον πελάτη **{cust_name_clean}** καταχωρήθηκε!")
                st.session_state['df_tr_xalia'] = pd.DataFrame()
                st.rerun()

    # =========================================================
    # 🏪 ΕΡΓΑΣΙΑ 2: ΠΑΡΑΔΟΣΗ ΡΟΥΧΩΝ ΣΤΟ ΜΑΓΑΖΙ (Ρούχα -> TrItems)
    # =========================================================
    else:
        st.markdown("##### 🏪 Στοιχεία Ρούχου / Είδους (Μαγαζί)")

        col_name_key = 'ItName' if 'ItName' in df_items.columns else 'Name'
        raw_items = df_items[col_name_key].dropna().tolist() if not df_items.empty and col_name_key in df_items.columns else ["Παντελόνι", "Πουκάμισο"]
        selected_item = st.selectbox("🏷️ Είδος Ρούχου", ["-- Επιλέξτε Είδος --"] + raw_items, key="shop_item")

        default_price = 0.0
        if selected_item != "-- Επιλέξτε Είδος --" and not df_items.empty:
            matched_item = df_items[df_items[col_name_key] == selected_item]
            if not matched_item.empty and 'Price' in matched_item.columns:
                default_price = float(matched_item['Price'].values[0] or 0.0)

        col1, col2, col3 = st.columns(3)
        with col1:
            total_price = st.number_input("💰 Τελική Τιμή (€)", min_value=0.0, step=0.5, value=default_price, key="shop_total")
        with col2:
            shelf = st.text_input("📍 Ράφι / Θέση", value="Ράφι Μαγαζιού", key="shop_shelf")
        with col3:
            status = st.selectbox("🔄 Κατάσταση", STATUS_OPTIONS, index=2, key="shop_status")

        if st.button("💾 Καταχώρηση Ρούχου στο Μαγαζί", type="primary"):
            if selected_customer_str == "-- Επιλέξτε Πελάτη --":
                st.error("❌ Επιλέξτε πελάτη!")
            elif selected_item == "-- Επιλέξτε Είδος --":
                st.error("❌ Επιλέξτε είδος!")
            else:
                cust_name_clean = selected_customer_str.split(" (")[0]
                today_str = datetime.now().strftime("%Y-%m-%d %H:%M")

                ws_tritems = get_worksheet("TrItems")
                next_id = 1 if df_tr_items.empty or 'TransactionID' not in df_tr_items.columns else int(df_tr_items['TransactionID'].max()) + 1

                ws_tritems.append_row([
                    next_id, cust_name_clean, selected_item, shelf, today_str, "", total_price, status
                ])
                st.success(f"✅ Το ρούχο για τον πελάτη **{cust_name_clean}** καταχωρήθηκε!")
                st.session_state['df_tr_items'] = pd.DataFrame()
                st.rerun()

def render_active_transactions_tab(df_tr_items, df_tr_xalia, df_customers, get_worksheet):
    sub_tab_x, sub_tab_c = st.tabs(["🚛 Χαλιά (Φορτηγό/Αποθήκη)", "🏪 Ρούχα (Μαγαζί)"])
    with sub_tab_x:
        _render_active_list(df_tr_xalia, "TrXalia", get_worksheet)
    with sub_tab_c:
        _render_active_list(df_tr_items, "TrItems", get_worksheet)

def _render_active_list(df_trans, sheet_name, get_worksheet_fn):
    if df_trans.empty or 'Status' not in df_trans.columns:
        st.info("Δεν υπάρχουν εγγραφές.")
        return

    active_data = df_trans[df_trans['Status'] != 'Παραδόθηκε']
    if active_data.empty:
        st.info("Δεν υπάρχουν εκκρεμότητες.")
        return

    ws = get_worksheet_fn(sheet_name)

    for idx, row in active_data.iterrows():
        c_name = row.get('CustomerName', row.get('CustomerID', 'Άγνωστος'))

        with st.expander(f"#{int(row['TransactionID'])} - {c_name} | {row.get('ItName', '')}"):
            st.write(f"📍 **Θέση/Ράφι:** {row.get('Place', '-')}")
            st.write(f"💶 **Τελική Τιμή:** {row.get('TotalPrice', 0)}€")

            curr_st = row.get('Status', STATUS_OPTIONS[0])
            new_st = st.selectbox(
                "Αλλαγή Κατάστασης", STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(curr_st) if curr_st in STATUS_OPTIONS else 0,
                key=f"st_{sheet_name}_{row['TransactionID']}"
            )
            
            if new_st != curr_st:
                # Υπολογισμός ακριβούς γραμμής στο Google Sheet (idx + 2) - Τέλεια απόδοση ακόμα και με 60.000+ γραμμές
                sheet_row_number = idx + 2
                
                status_col_idx = df_trans.columns.get_loc("Status") + 1
                ws.update_cell(sheet_row_number, status_col_idx, new_st)
                
                if new_st == "Παραδόθηκε" and 'DateOut' in df_trans.columns:
                    dateout_col_idx = df_trans.columns.get_loc("DateOut") + 1
                    ws.update_cell(sheet_row_number, dateout_col_idx, datetime.now().strftime("%Y-%m-%d %H:%M"))
                
                st.success("✅ Ενημερώθηκε επιτυχώς!")
                st.rerun()
