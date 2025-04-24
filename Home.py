import streamlit as st
import classes.db.initalize_database as initialize_database

# Initialize the database
initialize_database.InitializeDatabase().create_database()

# Set page configuration - simpler approach
st.set_page_config(
    page_title="ACPN2025", 
    layout="wide",
    page_icon="🚗"
)

# Title
st.title("Welcome to the Ryan² ACPN 2025 Demo! 🚗❤️🤖")

# Gradient text - simplified CSS
st.markdown("""
<style>
.gradient-text {
    background: linear-gradient(90deg, #ff7e5f, #feb47b);
    background-clip: text;
    -webkit-background-clip: text;
    color: transparent;
    font-weight: bold;
    font-size: 1.2em;
}
</style>
<p class="gradient-text">Bringing AI to the Automotive Aftermarket!</p>
""", unsafe_allow_html=True)

# Content
st.write("""
💡 We're showcasing practical, day-to-day applications of AI within the automotive aftermarket industry using off-the-shelf technology.

This is a **live showcase** that demonstrates real AI tools you can implement today to:
* 🔍 Streamline content management
* 📊 Improve data quality 
* 🛠️ Enhance your catalog operations

⬅️ Use the sidebar to navigate between different demos and examples.
📱 If you are on mobile, you may need to hit the arrow (>) to open the sidebar.
         
🤝 Feel free to reach out to either Ryan with any questions!
""")
