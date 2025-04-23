import streamlit as st

st.header("Dashboard")
st.write("This is the dashboard tab. Add stats, charts, or controls here.")

# Example UI
st.metric("Users", 120)
st.metric("Active Sessions", 7)
st.button("Refresh Data")
