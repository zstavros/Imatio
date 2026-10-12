def render_admin_view():
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        st.subheader("🔒 Περιοχή Διαχειριστή")
        entered_pass = st.text_input("Εισάγετε Κωδικό Διαχειριστή", type="password")
        
        if st.button("🔑 Σύνδεση", type="primary"):
            if entered_pass == "#G1orgos#":
                st.session_state.admin_logged_in = True
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("❌ Λανθασμένος κωδικός πρόσβασης.")
        return

    # Όταν είναι συνδεδεμένος:
    col1, col2 = st.columns([0.75, 0.25])
    with col1:
        st.subheader("🛠️ Πίνακας Ελέγχου")
    with col2:
        if st.button("🚪 Έξοδος"):
            st.session_state.admin_logged_in = False
            st.cache_data.clear()
            st.rerun()

    # ... υπόλοιπος κώδικας για τις 5 καρτέλες ...
