import streamlit as st

st.header("Analysis")
st.write("This is the analysis tab. Add your visualizations, filters, or results here.")

# Example UI
option = st.selectbox("Choose data set", ["Set A", "Set B"])
st.line_chart([1, 2, 3, 4, 3, 2, 4])
st.button("Run Analysis")
