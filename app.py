hide_streamlit_style = """
    <style>
    /* Απόκρυψη στοιχείων Streamlit */
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    .stAppFooter {display: none !important;}
    
    /* Μηδενισμός περιθωρίων στην κορυφή για να ανέβει τέρματα πάνω */
    .block-container {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    header {
        visibility: hidden !important;
        height: 0px !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)hide_streamlit_style = """
    <style>
    /* Απόκρυψη στοιχείων Streamlit */
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    .stAppFooter {display: none !important;}
    
    /* Μηδενισμός περιθωρίων στην κορυφή για να ανέβει τέρματα πάνω */
    .block-container {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    header {
        visibility: hidden !important;
        height: 0px !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
