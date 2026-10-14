st.markdown("### 🎛️ Κεντρικό Μενού Διαχείρισης")
st.write("Επιλέξτε την ενέργεια που επιθυμείτε:")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚛 Γρήγορη Φόρτωση Χαλιών", use_container_width=True):
        st.session_state['active_subview'] = 'fast_loading'
        st.rerun()
        
    if st.button("✏️ Τροποποίηση / Διαχείριση Χαλιών", use_container_width=True):
        st.session_state['active_subview'] = 'edit_xalia'
        st.rerun()

with col2:
    if st.button("👕 Καταχώρηση Ρούχων", use_container_width=True):
        st.session_state['active_subview'] = 'item_loading'
        st.rerun()
        
    if st.button("✏️ Τροποποίηση / Διαχείριση Ρούχων", use_container_width=True):
        st.session_state['active_subview'] = 'edit_items'
        st.rerun()
