elif st.session_state['active_subview'] == 'analytics':
    col_btn, _ = st.columns([1, 4])
    with col_btn:
        if st.button("🏠 ΑΡΧΙΚΗ", use_container_width=True):
            st.session_state['active_subview'] = 'menu'
            st.rerun()
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
    
    df_xalia = st.session_state.get('df_tr_xalia', pd.DataFrame())
    df_items = st.session_state.get('df_tr_items', pd.DataFrame())
    df_cust = st.session_state.get('df_customers', pd.DataFrame())

    today = date.today()

    if 'date_from' not in st.session_state:
        st.session_state['date_from'] = today.replace(day=1)
    if 'date_to' not in st.session_state:
        st.session_state['date_to'] = today

    st.subheader("📅 Επιλογή Χρονικού Διαστήματος (για τα Οικονομικά)")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📆 ΣΗΜΕΡΑ", use_container_width=True):
            st.session_state['date_from'] = today
            st.session_state['date_to'] = today
            st.rerun()
    with c2:
        if st.button("🗓️ ΤΡΕΧΩΝ ΜΗΝΑΣ", use_container_width=True):
            st.session_state['date_from'] = today.replace(day=1)
            st.session_state['date_to'] = today
            st.rerun()
    with c3:
        if st.button("📊 ΤΡΕΧΟΝ ΕΤΟΣ", use_container_width=True):
            st.session_state['date_from'] = today.replace(month=1, day=1)
            st.session_state['date_to'] = today
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        date_from = st.date_input("Από Ημερομηνία:", value=st.session_state['date_from'])
        st.markdown(f"📌 **Επιλεγμένη:** `{format_greek_date(pd.to_datetime(date_from))}`")
    with f_col2:
        date_to = st.date_input("Έως Ημερομηνία:", value=st.session_state['date_to'])
        st.markdown(f"📌 **Επιλεγμένη:** `{format_greek_date(pd.to_datetime(date_to))}`")

    t_from = pd.to_datetime(date_from)
    t_to = pd.to_datetime(date_to) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

    def process_df_revenue(df):
        if df.empty:
            return pd.DataFrame()
        df_filtered = df.copy()
        
        if 'DateOut' in df_filtered.columns:
            df_filtered['DateOut'] = pd.to_datetime(df_filtered['DateOut'], errors='coerce', dayfirst=True)
            df_filtered = df_filtered[(df_filtered['DateOut'] >= t_from) & (df_filtered['DateOut'] <= t_to)]

        if 'Status' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['Status'].astype(str).str.strip() == "Παραδόθηκε"]

        if 'TotalPrice' in df_filtered.columns:
            df_filtered['Price'] = df_filtered['TotalPrice'].apply(parse_price)
        else:
            df_filtered['Price'] = 0.0
            
        return df_filtered

    def process_df_top(df):
        if df.empty:
            return pd.DataFrame()
        df_filtered = df.copy()
        
        if 'Status' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['Status'].astype(str).str.strip() == "Παραδόθηκε"]

        if 'TotalPrice' in df_filtered.columns:
            df_filtered['Price'] = df_filtered['TotalPrice'].apply(parse_price)
        else:
            df_filtered['Price'] = 0.0
            
        return df_filtered

    filtered_xalia_rev = process_df_revenue(df_xalia)
    filtered_items_rev = process_df_revenue(df_items)

    filtered_xalia_top = process_df_top(df_xalia)
    filtered_items_top = process_df_top(df_items)

    revenue_xalia = filtered_xalia_rev['Price'].sum() if not filtered_xalia_rev.empty else 0.0
    revenue_items = filtered_items_rev['Price'].sum() if not filtered_items_rev.empty else 0.0
    total_revenue = revenue_xalia + revenue_items

    str_from_gr = format_greek_date(pd.to_datetime(date_from))
    str_to_gr = format_greek_date(pd.to_datetime(date_to))

    st.markdown("---")
    st.subheader(f"💰 Οικονομικά Αποτελέσματα (Παραδόθηκε) ({str_from_gr} - {str_to_gr})")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Έσοδα από Χαλιά", f"{revenue_xalia:,.2f} €")
    m2.metric("Έσοδα από Ρούχα", f"{revenue_items:,.2f} €")
    m3.metric("Συνολικός Τζίρος", f"{total_revenue:,.2f} €")
