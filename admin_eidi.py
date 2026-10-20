import streamlit as st
import pandas as pd
from datetime import datetime

STATUS_OPTIONS = ["Πλύσιμο", "Φύλαξη", "Πλύσιμο & Φύλαξη", "Έτοιμο", "Παραδόθηκε"]
# --- 1. ΤΡΟΠΟΠΟΙΗΣΗ ΧΑΛΙΩΝ (TrXalia) ---
def render_edit_xalia_tab(df_xalia, df_customers, df_items, get_worksheet_fn):
    st.markdown("### 🔍 Αναζήτηση & Τροποποίηση Χαλιών (TrXalia)")
    
    if df_xalia.empty:
        st.info("Den vrethikan eggrafes sta Xalia.")
        return

    # 1. Eksairoume oristika oses eggrafes einai "Paradothei"
    df_active = df_xalia[df_xalia['Status'] != 'Παραδόθηκε'].copy()
    
    # 2. Filtrarisma me ti stili Category apo ta Items
    if not df_items.empty:
        df_items.columns = df_items.columns.str.strip()
        
        col_name_key = next((ik for ik in ['ItName', 'Name', 'ItemName'] if ik in df_items.columns), None)
        col_cat_key = next((ck for ck in ['Category', 'CAT', 'CategoryName'] if ck in df_items.columns), None)
        
        if col_name_key and col_cat_key:
            xalia_items_list = df_items[
                df_items[col_cat_key].astype(str).str.strip().str.lower() == "χαλιά"
            ][col_name_key].dropna().astype(str).str.strip().tolist()
            
            if xalia_items_list:
                df_active = df_active[
                    df_active['ItName'].astype(str).str.strip().isin(xalia_items_list)
                ]

    if df_active.empty:
        st.success("🎉 Den yparxoun ekkremotites sta xalia!")
        return

    # Pedio Anazitisis
    search_query = st.text_input("🔎 Anazitisi me Onoma Pelati, Kinito/Tilefono i Barcode:", key="search_xalia_input")

    # 3. Etoimazoume ta tilefona pelaton
    cust_phone_map = {}
    if not df_customers.empty:
        df_cust_copy = df_customers.copy()
        df_cust_copy.columns = df_cust_copy.columns.str.strip()
        c_name_col = next((c for c in ['CuName', 'Name', 'CustomerName'] if c in df_cust_copy.columns), None)
        
        if c_name_col:
            for _, c_row in df_cust_copy.iterrows():
                cust_name = str(c_row[c_name_col]).strip()
                phones = []
                for p_col in ['CuMobile', 'CuPhone', 'Mobile', 'Phone', 'TEL', 'Τηλέφωνο']:
                    if p_col in df_cust_copy.columns and pd.notnull(c_row[p_col]):
                        clean_p = str(c_row[p_col]).replace(" ", "").replace("-", "").replace("+", "").replace("(", "").replace(")", "").strip()
                        if clean_p:
                            phones.append(clean_p)
                cust_phone_map[cust_name] = " ".join(phones)

    # 4. Ektelesi Anazitisis
    if search_query:
        q_raw = search_query.strip().lower()
        q_clean_num = q_raw.replace(" ", "").replace("-", "").replace("+", "").replace("(", "").replace(")", "")

        def match_row(row):
            c_name = str(row.get('CustomerName', '')).strip().lower()
            code_val = str(row.get('Code', '')).strip().lower()
            phone_val = cust_phone_map.get(str(row.get('CustomerName', '')).strip(), '').lower()

            match_name = q_raw in c_name
            match_code = q_raw in code_val
            match_phone = (q_clean_num in phone_val) if q_clean_num else False

            return match_name or match_code or match_phone

        df_filtered = df_active[df_active.apply(match_row, axis=1)]
    else:
        df_filtered = df_active

    if df_filtered.empty:
        st.warning("⚠️ Den vrethikan energes eggrafes me ta kritiria pou dosate.")
        return

    st.write(f"Vrethikan **{len(df_filtered)}** energes eggrafes:")
    ws = get_worksheet_fn("TrXalia")

    # 5. Emfanisi eggrafwn
    for idx, row in df_filtered.iterrows():
        tr_id = str(row['TransactionID'])
        c_name = row.get('CustomerName', 'Agnostos')
        code_val = str(row.get('Code', '-'))
        place_val = row.get('Place', row.get('Shelf', '-'))
        status_val = row.get('Status', '-')
        item_name = row.get('ItName', '')
        phone_show = cust_phone_map.get(c_name, '-')

        expander_label = f"📌 ID: #{tr_id} | {c_name} ({phone_show}) | Barcode: {code_val} | Θέση: {place_val} | Κατάσταση: {status_val} | {item_name}"

        with st.expander(expander_label):
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                new_len = st.text_input("Mikos (m)", value=str(row.get('Length', '')), key=f"len_{tr_id}_{idx}")
            with col2:
                new_hei = st.text_input("Ypsos (m)", value=str(row.get('Height', '')), key=f"hei_{tr_id}_{idx}")
            with col3:
                new_place = st.text_input("Thesi", value=str(place_val), key=f"plc_{tr_id}_{idx}")
            with col4:
                try:
                    curr_pr = float(row.get('TotalPrice', 0.0))
                except:
                    curr_pr = 0.0
                new_price = st.number_input("Timi (€)", value=curr_pr, step=1.0, key=f"prc_{tr_id}_{idx}")
            with col5:
                curr_st = row.get('Status', STATUS_OPTIONS[0])
                new_st = st.selectbox(
                    "Katastasi", STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(curr_st) if curr_st in STATUS_OPTIONS else 0,
                    key=f"st_x_{tr_id}_{idx}"
                )

            if st.button("💾 Apothikefsi Allagon", key=f"btn_save_x_{tr_id}_{idx}", type="primary"):
                try:
                    # Anazitisi akrivos tis grammis sto Google Sheet me vasi to TransactionID kai ton Code oste na min mperdevei tis seires
                    all_records = ws.get_all_records()
                    sheet_row = -1
                    
                    for r_idx, sheet_r in enumerate(all_records):
                        # Elegxoume oti to TransactionID kai o Code tairiazoun apolyta me tin eggrafi pou swzoume
                        if str(sheet_r.get('TransactionID', '')) == tr_id and str(sheet_r.get('Code', '')) == code_val:
                            sheet_row = r_idx + 2  # +2 dioti to get_all_records ksekinaei meta to header (grammi 1)
                            break
                    
                    if sheet_row == -1:
                        # Fallback an den vrei to syndyasmo, vriskei me to id tis seiras
                        sheet_row = idx + 2

                    cols = df_xalia.columns.tolist()
                    if "Length" in cols:
                        ws.update_cell(sheet_row, cols.index("Length") + 1, new_len)
                    if "Height" in cols:
                        ws.update_cell(sheet_row, cols.index("Height") + 1, new_hei)
                    
                    place_col_name = "Place" if "Place" in cols else ("Shelf" if "Shelf" in cols else None)
                    if place_col_name:
                        ws.update_cell(sheet_row, cols.index(place_col_name) + 1, new_place)

                    if "TotalPrice" in cols:
                        ws.update_cell(sheet_row, cols.index("TotalPrice") + 1, new_price)
                    if "Status" in cols:
                        ws.update_cell(sheet_row, cols.index("Status") + 1, new_st)
                        if new_st == "Παραδόθηκε" and "DateOut" in cols:
                            ws.update_cell(sheet_row, cols.index("DateOut") + 1, datetime.now().strftime("%Y-%m-%d %H:%M"))

                    # Xanofortoume ta dedomena amesws apo to Google Sheet
                    updated_data = ws.get_all_records()
                    st.session_state['df_tr_xalia'] = pd.DataFrame(updated_data) if updated_data else pd.DataFrame()
                    
                    st.success("✅ I enimerosi egine epityxos stin sosti eggrafi!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Sfalma apothikefsis: {e}")
