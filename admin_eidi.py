# Emfanisi eggrafwn me ti nea morfi ston titlo tou expander
    for idx, row in df_filtered.iterrows():
        tr_id = str(row['TransactionID'])
        c_name = row.get('CustomerName', 'Agnostos')
        code_val = row.get('Code', '-')
        place_val = row.get('Place', row.get('Shelf', '-'))
        status_val = row.get('Status', '-')
        item_name = row.get('ItName', '')
        phone_show = cust_phone_map.get(c_name, '-')

        # Afairesi tis leksis Pelatis kai allagi tou Kodikos se Barcode
        expander_label = f"📌 ID: #{tr_id} | {c_name} ({phone_show}) | Barcode: {code_val} | Thesi: {place_val} | Katastasi: {status_val} | {item_name}"

        with st.expander(expander_label):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                new_len = st.text_input("Mikos (m)", value=str(row.get('Length', '')), key=f"len_{tr_id}_{idx}")
            with col2:
                new_hei = st.text_input("Ypsos (m)", value=str(row.get('Height', '')), key=f"hei_{tr_id}_{idx}")
            with col3:
                try:
                    curr_pr = float(row.get('TotalPrice', 0.0))
                except:
                    curr_pr = 0.0
                new_price = st.number_input("Timi (€)", value=curr_pr, step=1.0, key=f"prc_{tr_id}_{idx}")
            with col4:
                curr_st = row.get('Status', STATUS_OPTIONS[0])
                new_st = st.selectbox(
                    "Katastasi", STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(curr_st) if curr_st in STATUS_OPTIONS else 0,
                    key=f"st_x_{tr_id}_{idx}"
                )

            if st.button("💾 Apothikefsi Allagon", key=f"btn_save_x_{tr_id}_{idx}", type="primary"):
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
                    st.success("✅ I enimerosi egine epityxos!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Sfalma apothikefsis: {e}")
