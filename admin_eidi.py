import streamlit as st
import pandas as pd
from datetime import datetime

STATUS_OPTIONS = [
    "Έτοιμος για παραλαβή",
    "Προς επεξεργασία",
    "Προς φύλαξη",
    "Παραδόθηκε"
]

def render_admin_eidi_dashboard(load_tab_data, get_worksheet):
    # CSS: Μεγάλα γράμματα ΜΟΝΟ στις καρτέλες (tabs) και μηδενισμός περιθωρίων
    st.markdown("""
        <style>
        header {display: none !important;}
        [data-testid="stHeader"] {display: none !important; height: 0px !important;}
        [data-testid="stToolbar"] {display: none !important;}
        footer {display: none !important;}
        
        .block-container {
            padding-top: 0rem !important;
            margin-top: 0rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            padding-bottom: 0rem !important;
        }
        
        [data-baseweb="tab"] p {
            font-size: 1.2rem !important;
            font-weight: 600 !important;
        }
        [data-baseweb="tab"] {
            font-size: 1.2rem !important;
        }
        
        div.stTextInput input {
            min-height: 28px !important;
            height: 28px !important;
            padding-top: 1px !important;
            padding-bottom: 1px !important;
            font-size: 0.95rem !important;
        }
        
        div.stTextArea textarea {
            min-height: 85px !important;
            height: 85px !important;
            font-size: 0.95rem !important;
        }
        
        .stForm {
            padding: 2px !important;
            margin-bottom: 0px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    df_customers = load_tab_data("Customers")
    df_items = load_tab_data("Items")
    df_tr_items = load_tab_data("TrItems")
    df_tr_xalia = load_tab_data("TrXalia")

    # Μόνο οι καρτέλες Νέα και Ανοιχτά
    tab1, tab2 = st.tabs([
        "📝 Νέα", 
        "📋 Ανοιχτά"
    ])

    # --- 1. ΝΕΑ ΠΑΡΑΔΟΣΗ (Καταχώρηση πολλαπλών ειδών με data_editor) ---
    with tab1:
        category_type = st.selectbox("Κατηγορία", ["👕 Ρούχα (TrItems)", "🧺 Χαλιά (TrXalia)"], key="new_trans_category")

        name_col = 'CuName' if 'CuName' in df_customers.columns else 'Name'
        if df_customers.empty or name_col not in df_customers.columns:
            st.warning("⚠️ Δεν βρέθηκαν πελάτες. Παρακαλώ καταχωρήστε πελάτες από το κεντρικό μενού.")
            st.stop()
        
        cust_choices = ["-- Επιλέξτε Πελάτη --"]
        for _, row in df_customers.iterrows():
            if pd.notnull(row.get(name_col)) and str(row.get(name_col)).strip() != '':
                phone = row.get('CuMobile') if pd.notnull(row.get('CuMobile')) and str(row.get('CuMobile')).strip() != '' else row.get('CuPhone', '')
                cust_choices.append(f"{row[name_col]} ({phone})")

        selected_customer_str = st.selectbox("Επιλογή Πελάτη", cust_choices, key="sel_cust_new")

        # Επιλογές ειδών με πρώτο το "-- Επιλέξτε Είδος --"
        col_name_key = 'ItName' if 'ItName' in df_items.columns else 'Name'
        raw_items = df_items[col_name_key].dropna().tolist() if not df_items.empty and col_name_key in df_items.columns else ["Παντελόνι", "Πουκάμισο", "Μπλούζα", "Μπουφάν"]
        item_choices = ["-- Επιλέξτε Είδος --"] + raw_items

        st.markdown("<p style='font-size: 0.95rem; font-weight: bold; margin-bottom: 2px;'>Καταχώρηση Ειδών & Θέσεων (Προσθέστε γραμμές +):</p>", unsafe_allow_html=True)

        # Τελείως κενός αρχικός πίνακας
        if "editor_df" not in st.session_state:
            st.session_state.editor_df = pd.DataFrame(
                columns=["Είδος", "Θέση / Ράφι", "Κόστος (€)"]
            )

        # Dynamic data editor
        edited_df = st.data_editor(
            st.session_state.editor_df,
            num_rows="dynamic",
            column_config={
                "Είδος": st.column_config.SelectboxColumn(
                    "Είδος",
                    options=item_choices,
                    required=True,
                    default="-- Επιλέξτε Είδος --"
                ),
                "Θέση / Ράφι": st.column_config.TextColumn("Θέση / Ράφι", required=False),
                "Κόστος (€)": st.column_config.NumberColumn("Κόστος (€)", min_value=0.0, step=0.5, default=0.0)
            },
            key="multi_items_editor",
            use_container_width=True
        )

        initial_status = st.selectbox("Αρχική Κατάσταση για όλα", STATUS_OPTIONS, index=1, key="init_status_multi")

        if st.button("💾 Καταχώρηση Όλων των Ειδών", type="primary"):
            if selected_customer_str == "-- Επιλέξτε Πελάτη --":
                st.error("❌ Επιλέξτε πελάτη πρώτα!")
            elif edited_df.empty:
                st.error("❌ Δεν έχετε προσθέσει κανένα είδος στον πίνακα!")
            else:
                cust_name_clean = selected_customer_str.split(" (")[0]
                cust_id = int(df_customers[df_customers[name_col] == cust_name_clean]['CustomerID'].values[0])
                
                # Αυτόματη λήψη τρέχουσας ημερομηνίας και ώρας
                today_str = datetime.now().strftime("%Y-%m-%d %H:%M")

                ws_tr = get_worksheet("TrItems" if "Ρούχα" in category_type else "TrXalia")
                current_tr_df = df_tr_items if "Ρούχα" in category_type else df_tr_xalia
                
                next_trans_id = 1 if current_tr_df.empty or 'TransactionID' not in current_tr_df.columns else int(current_tr_df['TransactionID'].max()) + 1

                added_count = 0
                for _, row in edited_df.iterrows():
                    item_name = row.get("Είδος", "")
                    place = row.get("Θέση / Ράφι", "")
                    cost = float(row.get("Κόστος (€)", 0.0))

                    if str(item_name).strip() != "" and item_name != "-- Επιλέξτε Είδος --":
                        ws_tr.append_row([next_trans_id, cust_id, item_name, place, today_str, "", cost, initial_status])
                        next_trans_id += 1
                        added_count += 1

                if added_count > 0:
                    st.success(f"✅ Καταχωρήθηκαν επιτυχώς {added_count} είδη με ημερομηνία {today_str}!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("❌ Παρακαλώ επιλέξτε έγκυρο είδος στις γραμμές του πίνακα!")

    # --- 2. ΑΝΟΙΧΤΑ ---
    with tab2:
        sub_tab_c, sub_tab_x = st.tabs(["👕 Ρούχα", "🧺 Χαλιά"])
        with sub_tab_c:
            _render_active_list(df_tr_items, df_customers, "TrItems", get_worksheet)
        with sub_tab_x:
            _render_active_list(df_tr_xalia, df_customers, "TrXalia", get_worksheet)


def _render_active_list(df_trans, df_cust, sheet_name, get_worksheet_fn):
    if df_trans.empty or 'Status' not in df_trans.columns:
        st.info("Δεν υπάρχουν εγγραφές.")
        return

    active_data = df_trans[df_trans['Status'] != 'Παραδόθηκε']
    if active_data.empty:
        st.info("Δεν υπάρχουν εκκρεμότητες.")
        return

    ws = get_worksheet_fn(sheet_name)
    name_col = 'CuName' if 'CuName' in df_cust.columns else 'Name'

    for _, row in active_data.iterrows():
        cust_info = df_cust[df_cust['CustomerID'] == row['CustomerID']]
        c_name = cust_info[name_col].values[0] if not cust_info.empty else "Άγνωστος"

        with st.expander(f"#{int(row['TransactionID'])} - {c_name} | {row.get('ItName', '')}"):
            st.write(f"📍 **Θέση:** {row.get('Place', '-')}")
            st.write(f"💶 **Κόστος:** {row.get('TotalPrice', 0)}€")

            curr_st = row.get('Status', 'Προς επεξεργασία')
            new_st = st.selectbox(
                "Αλλαγή Κατάστασης", STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(curr_st) if curr_st in STATUS_OPTIONS else 1,
                key=f"st_{sheet_name}_{row['TransactionID']}"
            )
            if new_st != curr_st:
                cell = ws.find(str(row['TransactionID']))
                ws.update_cell(cell.row, df_trans.columns.get_loc("Status") + 1, new_st)
                if new_st == "Παραδόθηκε":
                    ws.update_cell(cell.row, df_trans.columns.get_loc("DateOut") + 1, datetime.now().strftime("%Y-%m-%d %H:%M"))
                st.toast("Ενημερώθηκε!")
                st.cache_data.clear()
                st.rerun()
