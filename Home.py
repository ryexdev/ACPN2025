import streamlit as st
import os

secret_value = os.getenv("TESTING2")

st.set_page_config(page_title="ACPN2025", layout="wide")
st.title("ACPN2025 Platform")
st.write("Welcome. Use the sidebar to navigate between tabs/pages.")
st.write("Secret Value:", secret_value)