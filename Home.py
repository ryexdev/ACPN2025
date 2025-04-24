import streamlit as st
import os
# Set page configuration
st.set_page_config(
    page_title="ACPN 2025", 
    layout="wide",
    page_icon="🚗♥🤖"  # Added favicon
)

# Title
st.write("""
# Welcome to the Ryan² ACPN 2025 Demo! 🚗♥🤖
""")

# Animated text effect using HTML/CSS - Repositioned
st.markdown("""
<style>
.gradient-text {
    background: linear-gradient(90deg, #ff7e5f, #feb47b, #7ee8fa, #80ff72);
    background-size: 300% 300%;
    background-clip: text;
    -webkit-background-clip: text;
    color: transparent;
    animation: gradient 6s ease infinite;
    font-weight: bold;
    font-size: 1.2em;
}
@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
</style>
<p class="gradient-text">Bringing AI to the Automotive Aftermarket!</p>
""", unsafe_allow_html=True)

# Content
st.write("""
💡 We're showcasing practical, day-to-day applications of AI 
within the automotive aftermarket industry using off-the-shelf technology.
✨ This is a **live showcase** that demonstrates real AI tools you can implement today to:
* 🔍 Streamline content management
* 📊 Improve data quality 
* 🛠️ Enhance your catalog operations
⬅️ Use the sidebar to navigate between different demos and examples.
📱 If you are on mobile, you may need to hit the arrow (>) to open the sidebar.
         
🤝 Feel free to reach out to either Ryan with any questions!
""")
