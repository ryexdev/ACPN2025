import streamlit as st
import os

st.header("PIES Descriptions")
st.write("This is the PIES Descriptions tab.")

st.header("Secret Test")
secret_test = os.environ['TESTING2']
st.write(f"Secret Test: {secret_test}")
