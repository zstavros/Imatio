import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource(ttl=300)
def get_gspread_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def load_tab_data(tab_name):
    client = get_gspread_client()
    sheet_url = st.secrets["spreadsheet_url"]
    sh = client.open_by_url(sheet_url)
    worksheet = sh.worksheet(tab_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

def get_worksheet(tab_name):
    client = get_gspread_client()
    sheet_url = st.secrets["spreadsheet_url"]
    sh = client.open_by_url(sheet_url)
    return sh.worksheet(tab_name)
