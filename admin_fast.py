import streamlit as st
import pandas as pd
from datetime import datetime

def render_fast_loading_tab(df_customers, df_items, get_worksheet):
    if not df_customers.empty:
        df_customers.columns = df_customers.columns.str.strip()

    st.markdown("<p style='font-weight: bold; font-size: 1.15rem;'>🚛 Γρήγορη Φόρτωση / Παραλαβή Χαλιών</p>", unsafe_allow_html=True)
    st.write("Καταχωρήστε μαζικά χαλιά από το φορτηγό με εύρος κωδικών (π.χ. από 1 έως 5).")

    if df_customers.empty:
        try:
            ws_cust = get_worksheet("Customers")
            df_customers = pd.DataFrame(ws_cust.get_all_records())
            if not df_customers.empty:
                df_customers.columns = df_customers.columns.str.strip()
        except Exception:
            pass

    name_col = 'CuName' if 'CuName' in df_customers.columns else ('Name' if 'Name' in df_customers.columns else (df_customers.columns[1] if len(df_customers.columns) > 1 else None))
    
    if df_customers.empty or not name_col:
        st.warning("⚠️ Δεν βρέθηκαν πελάτες. Καταχωρήστε πρώτα πελάτες.")
        return
    
    cust_choices = ["-- Επιλέξτε Πελάτη --"]
    for _, row in df_customers.iterrows():
        if pd.notnull(row.get(name_col)) and str(row.get(name_col)).strip() != '':
            phone = row.get('CuMobile') if pd.notnull(row.get('CuMobile')) and str(row.get('CuMobile')).strip() != '' else row.get('CuPhone', '')
            cust_choices.append(f"{row[name_col]} ({phone})")

    # Χρήση st.form για να καθαρίζουν τα πεδία αυτόματα και να αποτρέπονται τα διπλασιασξένα κλικ
    with st.form("fast_loading_form", clear_on_submit=True):
        selected_customer_str = st.selectbox("Επιλογή Πελάτη", cust_choices, key="fast_load_cust")

        col1, col2 = st.columns(2)
        with col1:
            from_code = st.number_input("Από Κωδικό (From Code)", min_value=1, value=1, step=1, key="fast_from_code")
        with col2:
            to_code = st.number_input("Έως Κωδικό (To Code)", min_value=1, value=5, step=1, key="fast_to_code")

        col_name_key = 'ItName' if 'ItName' in df_items.columns else 'Name'
        raw_items = df_items[col_name_key].dropna().tolist() if not df_items.empty and col_name_key in df_items.columns else ["Χαλί Μηχανής", "Χαλί Χειροποίητο", "Μοκέτα"]
        item_choices = ["-- Επιλέξτε Είδος Χαλιού --"] + raw_items
        
        selected_item = st.selectbox("Είδος Χαλιού", item_choices, key="fast_load_item")
        job_type = st.selectbox("Εργασία", ["Πλύσιμο", "Φύλαξη", "Πλύσιμο & Φύλαξη"], key="fast_load_job")

        submitted = st.form_submit_button("🚀 Μαζική Φόρτωση & Αποθήκευση", type="primary")

    if submitted:
        if selected_customer_str == "-- Επιλέξτε Πελάτη --":
            st.error("❌ Παρακαλώ επιλέξτε πελάτη!")
        elif selected_item == "-- Επιλέξτε Είδος Χαλιού --":
            st.error("❌ Παρακαλώ επιλέξτε είδος χαλιού!")
        elif from_code > to_code:
            st.error("❌ Ο 'Από Κωδικός' δεν μπορεί να είναι μεγαλύτερος από τον 'Έως Κωδικό'!")
        else:
            cust_name_clean = selected_customer_str.split(" (")[0]
            today_str = datetime.now().strftime("%Y-%m-%d %H:%M")

            try:
                ws_xalia = get_worksheet("TrXalia")
                
                # Ασφαλής υπολογισμός επόμενου TransactionID κατευθείαν από τα τρέχοντα δεδομένα της Google
                existing_data = ws_xalia.get_all_records()
                df_xalia = pd.DataFrame(existing_data)
                
                if not df_xalia.empty and 'TransactionID' in df_xalia.columns:
                    # Μετατρέπουμε σε numeric για αποφυγή σφαλμάτων σύγκρισης
                    df_xalia['TransactionID'] = pd.to_numeric(df_xalia['TransactionID'], errors='coerce')
                    next_trans_id = int(df_xalia['TransactionID'].max()) + 1 if not df_xalia['TransactionID'].dropna().empty else 1
                else:
                    next_trans_id = 1

                # Συγκεντρώνουμε όλες τις γραμμές σε μία λίστα για μαζική αποστολή (Batch Insert)
                rows_to_append = []
                added_count = 0
                for current_code in range(int(from_code), int(to_code) + 1):
                    rows_to_append.append([
                        next_trans_id,              # A: TransactionID
                        cust_name_clean,            # B: CustomerName
                        selected_item,              # C: ItName
                        str(current_code),          # D: Code
                        "", "", "", "",             # E, F, G, H: Κενά
                        "Αποθήκη (Προσωρινό)",      # I: Place
                        today_str,                  # J: DateIn
                        "",                         # K: DateOut
                        0.0,                        # L: TotalPrice
                        job_type                    # M: Status
                    ])
                    added_count += 1

                # Μία και μοναδική κλήση API για όλες τις γραμμές
                if rows_to_append:
                    ws_xalia.append_rows(rows_to_append)

                st.success(f"✅ Φορτώθηκαν επιτυχώς {added_count} τεμάχια (Κωδικοί από {from_code} έως {to_code})!")
                
                # Καθαρισμός του session state για να ξαναδιαβάσει τα νέα δεδομένα
                st.session_state['df_tr_xalia'] = pd.DataFrame()
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Σφάλμα κατά την αποθήκευση: **{e}**")
