# --- 3. KATAXORISI ROUXWN / EIDWN ---
def render_item_loading_tab(df_customers, df_items, get_worksheet_fn):
    if df_customers.empty:
        st.warning("⚠️ Δεν βρέθηκαν πελάτες.")
        return

    name_col = 'CuName' if 'CuName' in df_customers.columns else 'Name'
    cust_choices = ["-- Επιλέξτε Πελάτη --"] + df_customers[name_col].dropna().tolist()

    # Φιλτράρισμα ειδών αποκλειστικά για την κατηγορία "Ρούχα"
    item_choices = ["-- Επιλέξτε Είδος --"]
    if not df_items.empty:
        df_items.columns = df_items.columns.str.strip()
        col_name_key = next((ik for ik in ['ItName', 'Name', 'ItemName'] if ik in df_items.columns), None)
        col_cat_key = next((ck for ck in ['Category', 'CAT', 'CategoryName'] if ck in df_items.columns), None)
        
        if col_name_key and col_cat_key:
            roucha_items = df_items[
                df_items[col_cat_key].astype(str).str.strip().str.lower() == "ρούχα"
            ][col_name_key].dropna().astype(str).str.strip().tolist()
            if roucha_items:
                item_choices += roucha_items

    # Η φόρμα περιλαμβάνει τα πάντα, ώστε τα κουμπιά να είναι επάνω και να μην υπάρχει περίγραμμα
    with st.form("item_loading_form", clear_on_submit=True):
        # 1. Κουμπιά πλοήγησης και αποθήκευσης επάνω (ίδια διάταξη με τα χαλιά)
        col_nav, col_empty, col_save = st.columns([1, 1, 1])
        
        with col_nav:
            form_back = st.form_submit_button("🏠 ΑΡΧΙΚΗ", use_container_width=True)
            if form_back:
                st.session_state['active_subview'] = 'menu'
                st.rerun()

        with col_save:
            submitted = st.form_submit_button("💾 ΑΠΟΘΗΚΕΥΣΗ", use_container_width=True)

        st.markdown("### 👕 Καταχώρηση Ρούχων & Ειδών")
        
        sel_cust = st.selectbox("Πελάτης", cust_choices)
        sel_item = st.selectbox("Είδος", item_choices)
        shelf = st.text_input("Ράφι / Θέση")
        price = st.number_input("Τιμή (€)", min_value=0.0, step=0.5)
        status = st.selectbox("Εργασία / Κατάσταση", ["Πλύσιμο", "Στεγνό Καθάρισμα", "Σιδέρωμα"])

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
