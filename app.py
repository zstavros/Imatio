import streamlit as st
from views import render_customer_view, render_admin_view

st.set_page_config(
    page_title="ImatioApp", 
    page_icon="🧺", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {display: none !important;}
    footer {visibility: hidden !important;}
    .block-container { padding-top: 1rem !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🧺 ImatioApp")
user_role = st.radio("Επιλέξτε ρόλο:", ["📱 Πελάτης", "🔒 Διαχειριστής"], horizontal=True)
st.divider()

if user_role == "📱 Πελάτης":
    render_customer_view()
else:
    render_admin_view()
