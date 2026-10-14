import streamlit as st
import pandas as pd
from datetime import datetime

def render_fast_loading_tab(df_customers, df_items, get_worksheet):
    # --- CSS GIA STATHERI GRAMMI AKOMA KAI SE KINITO & LEUKO PLAISIO ---
    st.markdown("""
        <style>
            div[data-testid="stColumn"] {
                background-color: transparent !important;
                box-shadow: none !important;
                padding: 0px 3px !important;
            }
            /* Apotropeyume to stivagma ton stilon sto kinito oste na menoun panta stin idia seira */
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
            .header-card {
                background-color: #ffffff;
                border: 2px solid #2b3e50;
                border-radius: 4px;
                padding: 0px 5px;
                text-align: center;
                height: 42px;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0px 1px 3px rgba(0,0,0,0.04);
            }
            .header-card-title {
                font-weight: 600;
                font-size: 0.8rem; /* Prosarmozomeno megethos gia na xoraei sto kinito */
                color: #2b3e50;
                margin: 0;
                white-space: nowrap;
                font-family: "Source Sans Pro", sans-serif;
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
        st.warning("⚠️ Den vrethikan pelates. Kataxoriste proti pelates.")
        return
    
    cust_choices = ["-- Epilexte Pelati --"]
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

    raw_items = df_items[col_name_key].dropna().tolist() if not df_items.empty and col_name_key else ["Chali Mechanis", "Chali Cheiropoiito", "Moketa"]
    item_choices = ["-- Epilexte Eidos Chaliou --"] + raw_items

    # --- PANO GRAMMI: 3 ISOPOSES STHLES (1:1:1) ---
    col_nav, col_title, col_btn = st.columns([1, 1, 1])

    with col_nav:
        if st.button("⬅️ Epistrofi sto Kentriko Menu", use_container_width=True):
            st.session_state['active_subview'] = 'menu'
            st.rerun()

    with col_title:
        st.markdown(
            """
            <div class="header-card">
                <p class="header-card-title">🚛 Grigori Fortosi / Paralavi Chalion</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

    with col_btn:
        submitted = st.button("🚀 Maziki Fortosi & Apothikeysi", type="primary", use_container_width=True)

    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

    # --- FORMA KATAXORISIS ---
    selected_customer_str = st.selectbox("Epilogi Pelati", cust_choices, key="fast_load_cust")

    c1, c2 = st.columns(2)
    with c1:
        from_code = st.number_input("Apo Kodiko (From Code)", min_value=1, value=1, step=1, key="fast_from_code")
    with c2:
        to_code = st.number_input("Eos Kodiko (To Code)", min_value=1, value=5, step=1, key="fast_to_code")

    selected_item = st.selectbox("Eidos Chaliou", item_choices, key="fast_load_item")
    job_type = st.selectbox("Ergasia", ["Plysimo", "Fylaxi", "Plysimo & Fylaxi"], key="fast_load_job")

    if submitted:
        if selected_customer_str == "-- Epilexte Pelati --":
            st.error("❌ Parakalo epilexte pelati!")
        elif selected_item == "-- Epilexte Eidos Chaliou --":
            st.error("❌ Parakalo epilexte eidos chaliou!")
        elif from_code > to_code:
            st.error("❌ O 'Apo Kodikos' den borei na einai megaliteros apo ton 'Eos Kodiko'!")
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
                        "Apothiki (Prosorino)",   
                        today_str,                
                        "",                       
                        0.0,                      
                        job_type                  
                    ])
                    added_count += 1

                if rows_to_append:
                    ws_xalia.append_rows(rows_to_append)

                st.success(f"✅ Fortothikan epitychos {added_count} temachia (Kodikoi apo {from_code} eos {to_code})!")
                st.session_state['active_subview'] = 'menu'
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Sfalma kata tin apothikeysi: **{e}**")
