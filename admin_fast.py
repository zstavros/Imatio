import streamlit as st
import pandas as pd
from datetime import datetime

def render_fast_loading_tab(df_customers, df_items, get_worksheet):
    # --- CSS ΓΙΑ ΣΤΑΘΕΡΗ ΟΡΙΖΟΝΤΙΑ ΓΡΑΜΜΗ ΣΕ ΚΙΝΗΤΑ ---
    st.markdown("""
        <style>
            div[data-testid="stColumn"] {
                background-color: transparent !important;
                box-shadow: none !important;
                padding: 0px 2px !important;
            }
            /* Στοιχίζουμε τη μεσαία στήλη και την κατεβάζουμε λίγο πιο κάτω */
            div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
                display: flex !important;
                flex-direction: column !important;
                justify-content: center !important;
                align-items: center !important;
                margin-top: 6px !important; 
            }
            @media (max-width: 768px) {
                div[data-testid="stHorizontalBlock"] {
                    display: flex !important;
                    flex-direction: row !important;
                    flex-wrap: nowrap !important;
                }
                div[data-testid="stColumn"] {
                    flex: 1 1 0% !important;
                    min-width: 0 !important;
                }
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

    # --- ΠΑΝΩ ΓΡΑΜΜΗ: ΑΡΧΙΚΗ | ΤΙΤΛΟΣ ΜΕ ΠΡΑΣΙΝΟ BOLD & WRAP | ΑΠΟΘΗΚΕΥΣΗ ---
    col_nav, col_title, col_btn = st.columns([1, 1, 1])

    with col_nav:
        if st.button("🏠 ΑΡΧΙΚΗ", use_container_width=True):
            st.session_state['active_subview'] = 'menu'
            st.rerun()

    with col_title:
        st.markdown(
            """
            <div style="display: flex; align-items: center; justify-content: center; height: 100%;">
                <p style="font-weight: bold !important; font-size: 0.85rem !important; color: #27ae60 !important; margin: 0 !important; padding: 0 !important; text-align: center; line-height: 1.15 !important; white-space: normal !important; word-break: break-word; font-family: 'Source Sans Pro', sans-serif;">
                    ΠΑΡΑΛΑΒΗ<br>ΧΑΛΙΩΝ
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )

    with col_btn:
        submitted = st.button("💾 ΑΠΟΘΗΚΕΥΣΗ", type="primary", use_container_width=True)

    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    # --- ΦΟΡΜΑ ΚΑΤΑΧΩΡΗΣΗΣ ---
    selected_customer_str = st.selectbox("Επιλογή Πελάτη", cust_choices, key="fast_load_cust")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div style="color: #27ae60 !important; font-weight: bold !important; font-size: 15px !important; margin-bottom: 5px !important; display: block !important;">Από Κωδικό</div>', unsafe_allow_html=True)
        from_code = st.number_input("Από Κωδικό", min_value=1, value=1, step=1, key="fast_from_code", label_visibility="collapsed")
    with c2:
        st.markdown('<div style="color: #27ae60 !important; font-weight: bold !important; font-size: 15px !important; margin-bottom: 5px !important; display: block !important;">Έως Κωδικό</div>', unsafe_allow_html=True)
        to_code = st.number_input("Έως Κωδικό", min_value=1, value=5, step=1, key="fast_to_code", label_visibility="collapsed")

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
                        next_trans_id,            
                        cust_name_clean,          
                        selected_item,            
                        str(current_code),        
                        "", "", "", "",           
                        "Αποθήκη (Προσωρινό)",    
                        today_str,                
                        "",                       
                        0.0,                      
                        job_type                  
                    ])
                    added_count += 1

                if rows_to_append:
                    ws_xalia.append_rows(rows_to_append)

                st.success(f"✅ Φορτώθηκαν επιτυχώς {added_count} τεμάχια (Κωδικοί από {from_code} έως {to_code})!")
                st.session_state['active_subview'] = 'menu'
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Σφάλμα κατά την αποθήκευση: **{e}**")
