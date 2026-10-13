# ==========================================
# 🔒 ΟΘΟΝΗ ΔΙΑΧΕΙΡΙΣΤΗ (LOGIN & DASHBOARD)
# ==========================================
else:
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
    else:
        # Δημιουργία των 5 κεντρικών καρτελών στην κορυφή
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📝 Νέα", 
            "📋 Ανοιχτά", 
            "👥 Πελάτες", 
            "👕 Είδη", 
            "🧺 Χαλιά"
        ])

        # Επειδή το admin_eidi.py διαχειρίζεται τα Νέα & Ανοιχτά:
        with tab1:
            render_admin_eidi_dashboard(load_tab_data, get_worksheet)
        with tab2:
            render_admin_eidi_dashboard(load_tab_data, get_worksheet)

        # Επειδή το admin_egg.py διαχειρίζεται τους Πελάτες & Είδη:
        with tab3:
            render_admin_egg_dashboard(load_tab_data, get_worksheet)
        with tab4:
            render_admin_egg_dashboard(load_tab_data, get_worksheet)

        with tab5:
            st.info("ℹ️ Χρησιμοποιείται η κεντρική βάση ειδών (Items) για καταχώρηση χαλιών.")
