import streamlit as st
import classes.db.initalize_database as initialize_database

# Initialize the database
initialize_database.InitializeDatabase().create_database()

# Set page configuration - simpler approach
st.set_page_config(
    page_title="Ryan²", 
    layout="wide",
    page_icon="🚗"
)

# Title
st.title("Ryan² ACPN 2025 Demo 🚗❤️🤖")

st.markdown("""
<style>
@keyframes gradientMove {
    0% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
    100% {
        background-position: 0% 50%;
    }
}
.gradient-text {
    background: linear-gradient(270deg, #ff7e5f, #feb47b, #ff7e5f);
    background-size: 400% 400%;
    background-clip: text;
    -webkit-background-clip: text;
    color: transparent;
    font-weight: bold;
    font-size: 1.5em;
    animation: gradientMove 6s ease infinite;
}
</style>
<p class="gradient-text">Bringing AI to the Automotive Aftermarket!</p>
""", unsafe_allow_html=True)


# Content
st.write("""We're showcasing practical, day-to-day applications of AI within the automotive aftermarket industry using off-the-shelf technology.

⬅️ Use the sidebar to navigate between different demos and examples.

📱 If you are on mobile, you may need to hit the arrow (>) to open the sidebar.
         

Feel free to reach out to either Ryan with any questions!

[Ryan Bachman](https://www.linkedin.com/in/bachmanryan/)

[Ryan Henderson](https://www.linkedin.com/in/ryan-andrew-henderson/)
""")