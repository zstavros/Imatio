import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# 1. ΝΕΑ ΕΓΓΡΑΦΗ ΠΕΛΑΤΗ
# ---------------------------------------------------------
def render_new_customer_tab(df_customers, get_worksheet):
    st.markdown("### ➕ Νέα Εγγραφή Πελάτη")
    ws_customers = get_worksheet("Customers")

    with st.form("new_customer_form", clear_on_submit=True):
        n_name = st.text_input("Ονοματεπώνυμο *")
        n_mobile1 = st.text_input("Κινητό-1 (CuPhone)")
        n_mobile2 = st.text_input("Κινητό-2 (CuMobile)")
        n_address = st.text_input("Διεύθυνση (CuAddress)")
        n_email = st.text_input("Email (CuEmail)")
        n_notes = st.text_area("Σημειώσεις (CuNotes)")
        
        if st.form_submit_button("💾 Αποθήκευση Νέου Πελάτη", type="primary"):
            if not n_name.strip():
                st.error("❌ Παρακαλώ συμπληρώστε Όνομα.")
            else:
                cust_id = 1 if df_customers.empty or 'CustomerID' not in df_customers.columns else int(pd.to_numeric(df_customers['CustomerID'], errors='coerce').max() or 0) + 1
                ws_customers.append_row([
                    cust_id, n_name.strip(), n_address.strip(), "", str(n_mobile1).strip(), str(n_mobile2).strip(), n_email.strip(), n_notes.strip()
                ])
                st.success(f"✅ Ο πελάτης **{n_name}** αποθηκεύτηκε επιτυχώς!")
                st.cache_data.clear()
                st.rerun()

# ---------------------------------------------------------
# 2. ΤΡΟΠΟΠΟΙΗΣΗ ΠΕΛΑΤΗ
# ---------------------------------------------------------
def render_edit_customer_tab(df_customers, get_worksheet):
    st.markdown("### ✏️ Τροποποίηση Στοιχείων Πελάτη")
    ws_customers = get_worksheet("Customers")
    name_col = 'CuName' if 'CuName' in df_customers.columns else 'Name'

    if not df_customers.empty and name_col in df_customers.columns:
        valid_customers = df_customers[df_customers[name_col].astype(str).str.strip() != ""]
        cust_options = ["-- Επιλέξτε πελάτη για επεξεργασία --"] + [f"{r[name_col]} ({r.get('CuPhone', r.get('CuMobile', ''))})" for _, r in valid_customers.iterrows()]
        selected_c = st.selectbox("Αναζήτηση Πελάτη", cust_options, label_visibility="collapsed")

        if selected_c and selected_c != "-- Επιλέξτε πελάτη για επεξεργασία --":
            c_name_val = selected_c.split(" (")[0]
            c_row_data = valid_customers[valid_customers[name_col] == c_name_val].iloc[0]
            
            st.markdown("<hr style='margin: 8px 0px;'>", unsafe_allow_html=True)
            with st.form("edit_customer_form"):
                st.write(f"✏️ Επεξεργασία: **{c_name_val}**")
                e_name = st.text_input("Ονοματεπώνυμο", value=str(c_row_data.get('CuName', c_row_data.get('Name', ''))))
                e_mobile1 = st.text_input("Κινητό-1", value=str(c_row_data.get('CuPhone', '')))
                e_mobile2 = st.text_input("Κινητό-2", value=str(c_row_data.get('CuMobile', '')))
                e_address = st.text_input("Διεύθυνση", value=str(c_row_data.get('CuAddress', '')))
                e_email = st.text_input("Email", value=str(c_row_data.get('CuEmail', '')))
                e_notes = st.text_area("Σημειώσεις", value=str(c_row_data.get('CuNotes', '')))
                
                if st.form_submit_button("🔄 Ενημέρωση Στοιχείων"):
                    try:
                        cell = ws_customers.find(c_name_val)
                        ws_customers.update_cell(cell.row, df_customers.columns.get_loc(name_col) + 1, e_name)
                        ws_customers.update_cell(cell.row, 5, e_mobile1)
                        ws_customers.update_cell(cell.row, 6, e_mobile2)
                        ws_customers.update_cell(cell.row, 3, e_address)
                        ws_customers.update_cell(cell.row, 7, e_email)
                        ws_customers.update_cell(cell.row, 8, e_notes)
                        st.success("✅ Ενημερώθηκε!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Σφάλμα: {e}")

# ---------------------------------------------------------
# 3. ΝΕΟ ΕΙΔΟΣ ΚΑΤΑΛΟΓΟΥ
# ---------------------------------------------------------
def render_new_item_tab(df_items, get_worksheet):
    st.markdown("### ➕ Νέο Είδος Καταλόγου")
    ws_items = get_worksheet("Items")

    with st.form("new_item_form", clear_on_submit=True):
        it_name = st.text_input("Όνομα Είδους (π.χ. Μπουφάν)")
        it_desc = st.text_input("Περιγραφή / Κατηγορία")
        it_price = st.number_input("ΤΙΜΗ (€)", min_value=0.0, step=0.5)
        it_price_m2 = st.number_input("ΤΙΜΗ ΤΕΤΡΑΓΩΝΙΚΟΥ (€/m²)", min_value=0.0, step=0.5)
        
        if st.form_submit_button("Προσθήκη Είδους"):
            if not it_name:
                st.error("Βάλτε όνομα είδους.")
            else:
                item_id = 1 if df_items.empty or 'ItemID' not in df_items.columns else int(pd.to_numeric(df_items['ItemID'], errors='coerce').max() or 0) + 1
                ws_items.append_row([item_id, it_name, it_desc, it_price, it_price_m2])
                st.success("Το είδος προστέθηκε επιτυχώς!")
                st.cache_data.clear()
                st.rerun()

# ---------------------------------------------------------
# 4. ΤΡΟΠΟΠΟΙΗΣΗ ΚΑΤΑΛΟΓΟΥ
# ---------------------------------------------------------
def render_edit_item_tab(df_items, get_worksheet):
    st.markdown("### ✏️ Τροποποίηση Καταλόγου")
    ws_items = get_worksheet("Items")
    col_name_key = 'ItName' if 'ItName' in df_items.columns else 'Name'

    if df_items.empty or col_name_key not in df_items.columns:
        st.info("Δεν υπάρχουν αποθηκευμένα είδη.")
    else:
        valid_items = df_items[df_items[col_name_key].astype(str).str.strip() != ""]
        item_options = ["-- Επιλέξτε είδος --"] + valid_items[col_name_key].dropna().tolist()
        selected_it = st.selectbox("Αναζήτηση Είδους", item_options, label_visibility="collapsed", key="search_item_selectbox")

        if selected_it and selected_it != "-- Επιλέξτε είδος --":
            row_data = valid_items[valid_items[col_name_key] == selected_it].iloc[0]
            curr_price = float(row_data.get('Price', 0.0) or 0.0) if 'Price' in df_items.columns else 0.0
            curr_price_m2 = float(row_data.get('Price m2', row_data.get('Price_m2', 0.0)) or 0.0)

            with st.form("edit_item_form"):
                st.write(f"✏️ Επεξεργασία: **{selected_it}**")
                new_it_name = st.text_input("Όνομα Είδους", value=selected_it)
                new_price = st.number_input("ΤΙΜΗ (€)", value=curr_price, min_value=0.0, step=0.5)
                new_price_m2 = st.number_input("ΤΙΜΗ ΤΕΤΡΑΓΩΝΙΚΟΥ (€/m²)", value=curr_price_m2, min_value=0.0, step=0.5)
                
                if st.form_submit_button("Αποθήκευση Αλλαγών"):
                    try:
                        cell = ws_items.find(selected_it)
                        ws_items.update_cell(cell.row, 2, new_it_name)
                        ws_items.update_cell(cell.row, 3, new_price)
                        ws_items.update_cell(cell.row, 4, new_price_m2)
                        
                        st.success("✅ Το είδος ενημερώθηκε επιτυχώς!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Σφάλμα: {e}")
