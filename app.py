from admin_egg import render_admin_egg_dashboard  # Αντί για admin_views
from admin_eidi import render_admin_eidi_dashboard

# ... (όλος ο προηγούμενος κώδικας για το login και τον πελάτη παραμένει ίδιος) ...

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
        # Δημιουργία των 5 κεντρικών καρτελών στην κορυφή της οθόνης
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📝 Νέα", 
            "📋 Ανοιχτά", 
            "👥 Πελάτες", 
            "👕 Είδη", 
            "🧺 Χαλιά"
        ])

        # Καρτέλες 1 & 2: Διαχείριση κινήσεων από το admin_eidi.py
        with tab1:
            render_admin_eidi_dashboard(load_tab_data, get_worksheet)
        with tab2:
            # Το admin_eidi περιέχει και τις δύο καρτέλες (Νέα/Ανοιχτά), 
            # οπότε μπορούμε να καλούμε τη συνάρτηση ή να τη χωρίσουμε.
            # (Εναλλακτικά, αν η συνάρτηση render_admin_eidi_dashboard φτιάχνει και τα δύο tabs εσωτερικά, 
            # βλέπε παρακάτω την απλούστερη προσέγγιση).
