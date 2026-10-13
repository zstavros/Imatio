import streamlit as st
import pandas as pd
from datetime import datetime

def render_fast_loading_tab(df_customers, df_items, get_worksheet):
    st.markdown("<p style='font-weight: bold; font-size: 1.15rem;'>🚛 Γρήγορη Φόρτωση / Παραλαβή Χαλιών</p>", unsafe_allow_html=True)
    st.write("Καταχωρήστε μαζικά χαλιά από το φορτηγό με εύρος κωδικών (π.χ. από 1 έως 5).")

    # 1. Επιλογή Πελάτη
    name_col = 'CuName' if 'CuName' in df_customers.columns else 'Name'
    if df_customers.empty or name_col not in df_customers.columns:
        st.warning("⚠️ Δεν βρέθηκαν πελάτες. Καταχωρήστε πρώτα πελάτες.")
        return
    
    cust_choices = ["-- Επιλέξτε Πελάτη --"]
    for _, row in df_customers.iterrows():
        if pd.notnull(row.get(name_col)) and str(row.get(name_col)).strip() != '':
            phone = row.get('CuMobile') if pd.notnull(row.get('CuMobile')) and str(row.get('CuMobile')).strip() != '' else row.get('CuPhone', '')
            cust_choices.append(f"{row[name_col]} ({phone})")

    selected_customer_str = st.selectbox("Επιλογή Πελάτη", cust_choices, key="fast_load_cust")

    # 2. Εύρος Κωδικών (Από - Έως)
    col1, col2 = st.columns(2)
    with col1:
        from_code = st.number_input("Από Κωδικό (From Code)", min_value=1, value=1, step=1)
    with col2:
        to_code = st.number_input("Έως Κωδικό (To Code)", min_value=1, value=5, step=1)

    # 3. Είδος Χαλιού από τον τιμοκατάλογο
    col_name_key = 'ItName' if 'ItName' in df_items.columns else 'Name'
    raw_items = df_items[col_name_key].dropna().tolist() if not df_items.empty and col_name_key in df_items.columns else ["Χαλί Μηχανής", "Χαλί Χειροποίητο", "Μοκέτα"]
    item_choices = ["-- Επιλέξτε Είδος Χαλιού --"] + raw_items
    
    selected_item = st.selectbox("Είδος Χαλιού", item_choices, key="fast_load_item")

    # 4. Εργασία (Με menu που ανοίγει και διαλέγει: Πλύσιμο ή Φύλαξη)
    job_type = st.selectbox("Εργασία", ["Πλύσιμο", "Φύλαξη", "Πλύσιμο & Φύλαξη"], key="fast_load_job")

    # 5. Κμπυί Μαζικής Καταχώρησης
    if st.button("🚀 Μαζική Φόρτωση & Αποθήκευση", type="primary"):
        if selected_customer_str == "-- Επιλέξτε Πελάτη --":
            st.error("❌ Παρακαλώ επιλέξτε πελάτη!")
        elif selected_item == "-- Επιλέξτε Είδος Χαλιού --":
            st.error("❌ Παρακαλώ επιλέξτε είδος χαλιού!")
        elif from_code > to_code:
            st.error("❌ Ο 'Από Κωδικός' δεν μπορεί να είναι μεγαλύτερος από τον 'Έως Κωδικό'!")
        else:
            cust_name_clean = selected_customer_str.split(" (")[0]
            cust_id = int(df_customers[df_customers[name_col] == cust_name_clean]['CustomerID'].values[0])
            today_str = datetime.now().strftime("%Y-%m-%d %H:%M")

            # Συνδεόμαστε στο Google Sheet που θα αποθηκεύονται (π.χ. TrEidi ή TrXalia)
            ws_treidi = get_worksheet("TrEidi") # Μπορείς να χρησιμοποιήσεις και TrXalia αν θες
            
            # Παίρνουμε τα τρέχοντα δεδομένα για να βρούμε το επόμενο TransactionID
            existing_data = ws_treidi.get_all_records()
            df_treidi = pd.DataFrame(existing_data)
            next_trans_id = 1 if df_treidi.empty or 'TransactionID' not in df_treidi.columns else int(df_treidi['TransactionID'].max()) + 1

            added_count = 0
            # Δημιουργία βρόχου για το εύρος από -> έως
            for current_code in range(int(from_code), int(to_code) + 1):
                # Δομή εγγραφής: [TransactionID, CustomerID, ItemName, Code/A/A, JobType, DateIn, Place, Price, Status]
                # Η κατάσταση ορίζεται αυτόματα ως "Στην Αποθήκη"
                ws_treidi.append_row([
                    next_trans_id, 
                    cust_id, 
                    selected_item, 
                    str(current_code), # Ο κωδικός χαλιού (π.χ. 1, 2, 3...)
                    job_type, 
                    today_str, 
                    "Αποθήκη (Προσωρινό)", # Ράφι/Θέση αρχικά στην αποθήκη
                    0.0, # Κόστος (θα υπολογιστεί ή θα μπει αργότερα όταν μετρηθεί)
                    "Στην Αποθήκη"
                ])
                next_trans_id += 1
                added_count += 1

            st.success(f"✅ Φορτώθηκαν επιτυχώς {added_count} τεμάχια (Κωδικοί από {from_code} έως {to_code}) με κατάσταση **'Στην Αποθήκη'**!")
            st.cache_data.clear()
            st.rerun()
