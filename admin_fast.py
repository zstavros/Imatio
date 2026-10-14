import streamlit as st
import pandas as pd
from datetime import datetime

def render_fast_loading_tab(df_customers, df_items, get_worksheet):
    # --- STYLING ---
    st.markdown("""
        <style>
            .fast-title {
                color: #1b6338;
                font-size: 1.4rem;
                font-weight: 800;
                margin: 0;
                padding-top: 5px;
            }
            div[data-testid="stForm"] {
                background-color: #f4f6f9;
                border: 1px solid #d1d8e0;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }
        </style>
    """, unsafe_allow_html=True)

    if not df_customers.empty:
        df_customers.columns = df_customers.columns.str.strip()

    name_col = None
    for col in ['CuName', 'Name', 'CUSTOMER', 'CustomerName']:
        if not df_customers.empty and col in df_customers.columns:
            name_col = col
            break
            
    if not name_col and not df_customers.empty and len(df_customers.columns) > 1:
        name_col = df_customers.columns[1]

    if df_customers.empty or not name_col:
        st.warning("⚠️ Δεν βρέθηκαν πελάτες. Καταχωρίστε πρώτα πελάτες.")
        return
    
    cust_choices = ["-- Επιλέξτε Πελάτη --"]
    for _, row in df_customers.iterrows():
        val = row.get(name_col)
        if pd.notnull(val) and str(val).strip() != '':
            phone = ""
            for p_col in ['CuMobile', 'CuPhone', 'Mobile', 'Phone']:
                if p_col in row and pd.notnull(row[p_col]) and str(row[p_col]).strip() != '':
                    phone = str(row[p_col])
                    break
            if phone:
                cust_choices.append(f"{val} ({phone})")
            else:
                cust_choices.append(str(val))

    col_name_key = None
    if not df_items.empty:
        df_items.columns = df_items.columns.str.strip()
        for ik in ['ItName', 'Name', 'ItemName']:
            if ik in df_items.columns:
                col_name_key = ik
                break

    raw_items = df_items[col_name_key].dropna().tolist() if not df_items.empty and col_name_key else ["Χαλί Μηχανής", "Χαλί Χειροποίητο", "Μοκέτα"]
    item_choices = ["-- Επιλέξτε Είδος Χαλιού --"] + raw_items

    # --- TOP ROW: TITLE & SUBMIT BUTTON ---
    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.markdown('<p class="fast-title">🚛 Γρήγορη Φόρτωση / Παραλαβή Χαλιών</p>', unsafe_allow_html=True)

    with st.form("fast_loading_form", clear_on_submit=True):
        # Το κουμπί αποθήκευσης μπαίνει μέσα στη φόρμα αλλά το τοποθετούμε έξυπνα δεξιά
        # (ή το πατάει ο χρήστης από κάτω/πάνω ανάλογα με τη δομή της φόρμες)
        # Για να είναι το κουμπί ακριβώς δίπλα στον τίτλο πανω δεξιά:
        
        # Σημείωση: Στο Streamlit το st.form_submit_button πρέπει να είναι μέσα στο with st.form.
        # Οπότε βάζουμε μια γραμμή εσωτερικά για το κουμπί πάνω δεξιά.
        
        col_btn1, col_btn2 = st.columns([4, 1.2])
        with col_btn2:
            submitted = st.form_submit_button("🚀 Αποθήκευση", type="primary", use_container_width=True)

        selected_customer_str = st.selectbox("Επιλογή Πελάτη", cust_choices, key="fast_load_cust")

        c1, c2 = st.columns(2)
        with c1:
            from_code = st.number_input("Από Κωδικό (From Code)", min_value=1, value=1, step=1, key="fast_from_code")
        with c2:
            to_code = st.number_input("Έως Κωδικό (To Code)", min_value=1, value=5, step=1, key="fast_to_code")

        selected_item = st.selectbox("Είδος Χαλιού", item_choices, key="fast_load_item")
        job_type = st.selectbox("Εργασία", ["Πλύσιμο", "Φύλαξη", "Πλύσιμο & Φύλαξη"], key="fast_load_job")

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
                existing_data = ws_xalia.get_all_records()
                df_xalia = pd.DataFrame(existing_data)
                
                if not df_xalia.empty and 'TransactionID' in df_xalia.columns:
                    df_xalia['TransactionID'] = pd.to_numeric(df_xalia['TransactionID'], errors='coerce')
                    next_trans_id = int(df_xalia['TransactionID'].max()) + 1 if not df_xalia['TransactionID'].dropna().empty else 1
                else:
                    next_trans_id = 1

                rows_to_append = []
                added_count = 0
                for current_code in range(int(from_code), int(to_code) + 1):
                    rows_to_append.append([
                        next_trans_id,            # A: TransactionID
                        cust_name_clean,          # B: CustomerName
                        selected_item,            # C: ItName
                        str(current_code),        # D: Code
                        "", "", "", "",           # E, F, G, H: Κενά
                        "Αποθήκη (Προσωρινό)",    # I: Place
                        today_str,                # J: DateIn
                        "",                       # K: DateOut
                        0.0,                      # L: TotalPrice
                        job_type                  # M: Status
                    ])
                    added_count += 1

                if rows_to_append:
                    ws_xalia.append_rows(rows_to_append)

                st.success(f"✅ Φορτώθηκαν επιτυχώς {added_count} τεμάχια (Κωδικοί από {from_code} έως {to_code})!")
                st.session_state['df_tr_xalia'] = pd.DataFrame()
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Σφάλμα κατά την αποθήκευση: **{e}**")
