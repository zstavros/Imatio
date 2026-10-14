import streamlit as st
import pandas as pd
from datetime import datetime

def render_fast_loading_tab(df_customers, df_items, get_worksheet):
    # --- STYLING & COLOR COMBINATION ---
    st.markdown("""
        <style>
            .fast-header-box {
                background: linear-gradient(135deg, #1b6338 0%, #28804c 100%);
                padding: 14px 20px;
                border-radius: 10px;
                color: #ffffff;
                text-align: center;
                font-size: 1.25rem;
                font-weight: 700;
                margin-bottom: 20px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.15);
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

    # Prasino header psila sto kentro
    st.markdown('<div class="fast-header-box">🚛 Γρήγορη Φόρτωση / Παραλαβή Χαλιών</div>', unsafe_allow_html=True)

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
        st.warning("⚠️ Den vrethikan pelates. Kataxoriste proti pelates.")
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

    with st.form("fast_loading_form", clear_on_submit=True):
        selected_customer_str = st.selectbox("Επιλογή Πελάτη", cust_choices, key="fast_load_cust")

        col1, col2 = st.columns(2)
        with col1:
            from_code = st.number_input("Από Κωδικό (From Code)", min_value=1, value=1, step=1, key="fast_from_code")
        with col2:
            to_code = st.number_input("Έως Κωδικό (To Code)", min_value=1, value=5, step=1, key="fast_to_code")

        selected_item = st.selectbox("Είδος Χαλιού", item_choices, key="fast_load_item")
        job_type = st.selectbox("Εργασία", ["Πλύσιμο", "Φύλαξη", "Πλύσιμο & Φύλαξη"], key="fast_load_job")

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 Μαζική Φόρτωση & Αποθήκευση", type="primary", use_container_width=True)

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
