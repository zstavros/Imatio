import streamlit as st
import pandas as pd

# ==========================================
# 1. ΡΥΘΜΙΣΗ ΣΕΛΙΔΑΣ & SESSION STATE
# ==========================================
st.set_page_config(page_title="Καθαριστήριο - Διαχείριση", page_icon="🧺", layout="wide")

if "user_role" not in st.session_state:
    st.session_state["user_role"] = None  # 'admin' ή 'customer'
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

# ==========================================
# 2. ΣΥΝΔΕΣΗ GOOGLE OAUTH & ΔΙΑΧΕΙΡΙΣΗ
# ==========================================
def check_google_login():
    """Ελέγχει το Google Auth μέσω st.login() ή Streamlit Secrets."""
    # Αν ο χρήστης έχει ήδη συνδεθεί μέσω Streamlit OAuth
    if hasattr(st, "user") and st.user.is_logged_in:
        email = st.user.email
        allowed_admins = st.secrets["google_oauth"]["admin_emails"]
        if email in allowed_admins:
            st.session_state["user_role"] = "admin"
            st.session_state["user_email"] = email
            return True
        else:
            st.error(f"⛔ Το email {email} δεν έχει δικαιώματα διαχειριστή.")
            return False
    return False

# ==========================================
# 3. ΑΡΧΙΚΗ ΟΘΟΝΗ (LOGIN SCREEN)
# ==========================================
if st.session_state["user_role"] is None:
    st.title("🧺 Καλώς Ήρθατε στο Καθαριστήριο")
    st.subheader("Παρακαλώ επιλέξτε την ιδιότητά σας για να συνεχίσετε:")
    st.markdown("---")

    col1, col2 = st.columns(2)

    # 📱 ΕΙΣΟΔΟΣ ΠΕΛΑΤΗ
    with col1:
        st.info("### 📱 Είμαι Πελάτης")
        st.write("Δείτε άμεσα την κατάσταση των ρούχων & χαλιών σας με το κινητό σας.")
        phone_input = st.text_input("Πληκτρολογήστε το Κινητό Τηλέφωνο:", placeholder="6912345678")
        
        if st.button("🔎 Αναζήτηση Παραγγελίας", type="primary"):
            if phone_input.strip():
                st.session_state["user_role"] = "customer"
                st.session_state["customer_phone"] = phone_input.strip()
                st.rerun()
            else:
                st.warning("Παρακαλώ εισάγετε έναν έγκυρο αριθμό τηλεφώνου.")

    # 🔑 ΕΙΣΟΔΟΣ ΔΙΑΧΕΙΡΙΣΤΗ
    with col2:
        st.success("### 🔑 Είσοδος Διαχειριστή")
        st.write("Πρόσβαση σε όλες τις λειτουργίες, καταχωρίσεις και οικονομικές αναφορές.")
        
        # Αν χρησιμοποιείται το νέο st.login της Streamlit (έκδοση 1.40+)
        if hasattr(st, "login"):
            if st.button("🔐 Σύνδεση με Google", key="google_login_btn"):
                st.login()
        else:
            # Εναλλακτική χειροκίνητη επιβεβαίωση / fallback
            st.write("Πατήστε για ταυτοποίηση μέσω Google:")
            if check_google_login():
                st.rerun()

# ==========================================
# 4. ΟΘΟΝΗ ΠΕΛΑΤΗ (CUSTOMER VIEW)
# ==========================================
elif st.session_state["user_role"] == "customer":
    phone = st.session_state.get("customer_phone", "")
    
    st.sidebar.title(f"👤 Πελάτης: {phone}")
    if st.sidebar.button("🚪 Έξοδος"):
        st.session_state["user_role"] = None
        st.rerun()

    st.title("📦 Τα Έτοιμα Είδη Σας")
    st.write(f"Αναζήτηση για το τηλέφωνο: **{phone}**")
    st.markdown("---")

    # ΕΔΩ ΦΟΡΤΩΝΟΝΤΑΙ ΤΑ ΔΕΔΟΜΕΝΑ ΑΠΟ GOOGLE SHEETS
    # Παράδειγμα προσομοίωσης:
    ready_items = [
        {"Είδος": "Παντελόνι", "Τύπος": "Ρούχο", "Κατάσταση": "Έτοιμο", "Ημ. Παραλαβής": "2026-10-25"},
        {"Είδος": "Χαλί Μάλλινο", "Τύπος": "Χαλί", "Κατάσταση": "Έτοιμο", "Ημ. Παραλαβής": "2026-10-26"},
    ]
    
    if ready_items:
        df_ready = pd.DataFrame(ready_items)
        st.dataframe(df_ready, use_container_width=True)
        st.success("✨ Τα παραπάνω είδη είναι έτοιμα! Μπορείτε να περάσετε από το κατάστημα για παραλαβή.")
    else:
        st.info("Δεν βρέθηκαν έτοιμα είδη για αυτό το τηλέφωνο αυτή τη στιγμή.")

# ==========================================
# 5. ΟΘΟΝΗ ΔΙΑΧΕΙΡΙΣΤΗ (ADMIN DASHBOARD)
# ==========================================
elif st.session_state["user_role"] == "admin":
    admin_email = st.session_state.get("user_email", "Admin")
    
    st.sidebar.title("🛡️ Πάνελ Διαχειριστή")
    st.sidebar.caption(f"Συνδέθηκε ως: {admin_email}")
    
    menu = st.sidebar.radio(
        "Πλοήγηση Μενού:",
        ["📊 Αναφορές & Στατιστικά", "📝 Καταχώριση Παραγγελίας", "🚚 Παραδόσεις / Παραλαβές", "👥 Πελάτες"]
    )
    
    if st.sidebar.button("🚪 Αποσύνδεση"):
        if hasattr(st, "logout"):
            st.logout()
        st.session_state["user_role"] = None
        st.rerun()

    # --------------------------------------
    # ΕΝΟΤΗΤΑ: ΑΝΑΦΟΡΕΣ & ΣΤΑΤΙΣΤΙΚΑ
    # --------------------------------------
    if menu == "📊 Αναφορές & Στατιστικά":
        st.title("📊 Αναφορές & Στατιστικά Επιχείρησης")
        st.markdown("---")

        # Φίλτρο Περιόδου
        period = st.selectbox("Επιλέξτε Χρονική Περίοδο:", ["Ημερήσια", "Εβδομαδιαία", "Μηνιαία", "Ετήσια"])

        st.subheader(f"📈 Οικονομικός Τζίρος ({period})")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Έσοδα από Χαλιά", "450 €", "+12%")
        col_m2.metric("Έσοδα από Ρούχα", "320 €", "+5%")
        col_m3.metric("Συνολικός Τζίρος", "770 €", "+9%")

        st.markdown("---")
        
        col_left, col_right = st.columns(2)

        # TOP 10 ΠΕΛΑΤΕΣ
        with col_left:
            st.subheader("🏆 Top-10 Πελάτες")
            top_customers = pd.DataFrame({
                "Πελάτης": ["Γιώργος Π.", "Μαρία Κ.", "Νίκος Α.", "Ελένη Δ.", "Κώστας Μ."],
                "Συχνότητα": [12, 10, 8, 7, 5],
                "Συνολικός Τζίρος (€)": [450, 380, 310, 260, 200]
            })
            st.dataframe(top_customers, use_container_width=True)

        # TOP 5 ΕΙΔΗ (ΧΑΛΙΑ & ΡΟΥΧΑ)
        with col_right:
            st.subheader("🥇 Top-5 Δημοφιλή Είδη")
            tab_carpets, tab_clothes = st.tabs(["🧶 Χαλιά", "👔 Ρούχα"])
            
            with tab_carpets:
                top_carpets = pd.DataFrame({
                    "Είδος Χαλιού": ["Μάλλινο", "Μηχανής", "Μεταξωτό", "Διάδρομος", "Ψάθα"],
                    "Τεμάχια": [85, 62, 40, 35, 18]
                })
                st.dataframe(top_carpets, use_container_width=True)

            with tab_clothes:
                top_clothes = pd.DataFrame({
                    "Είδος Ρούχου": ["Κοστούμι", "Παντελόνι", "Παπλωμα", "Πουκάμισο", "Μπουφάν"],
                    "Τεμάχια": [140, 115, 90, 85, 60]
                })
                st.dataframe(top_clothes, use_container_width=True)

    else:
        st.title(f"📌 Ενότητα: {menu}")
        st.info("Εδώ βρίσκονται οι υπόλοιπες λειτουργίες του προγράμματος.")
