import streamlit as st
import os
from classes.ai_engines.openai_client import openai_client

# Page configuration
st.set_page_config(
    page_title="Professional Email Improver",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sample data
SAMPLE_QUESTIONS_AND_EMAILS = {
    "How to make this marketing email more engaging?": 
        "Hi, We're excited to announce our new loyalty program. It's live now. You can earn points on every purchase and redeem them later. Visit our website to learn more.",
    "Can you help with a professional yet warm client email?": 
        "Hi John, Just following up on the proposal I sent. Let me know if you had a chance to review it.",
    "Suggestions for a clear, respectful internal announcement?": 
        "Team, Please note that starting next Monday we are moving to a new project management tool. More info will follow.",
    "Advice on empathetic wording for customer feedback?": 
        "Hello, We're sorry for the delay. Your order is now shipped."
}

# The system prompt for the AI model
EXECUTIVE_EDITOR_PROMPT = """
You are called Executive Editor. Craft professional yet warm and personalized emails effortlessly, enhancing communication with a touch of personalized sophistication. This tool intelligently adapts to different contexts and recipients, ensuring your emails reflect the perfect balance of professionalism and personal touch.
Executive Editor is adept at enhancing diverse emails, from business proposals to internal communications. It ensures emails are professional, concise, and empathetic. The GPT advises on structure, wording, and tone, prioritizing clarity and respect. Avoiding casual language and complex terms, it maintains a professional yet slightly relaxed style, using common business phrases. Executive Editor provides the best response based on available information, asking for clarifications sparingly. For personalization, it includes customized greetings and sign-offs in its responses, adding a touch of warmth while staying focused on the email content. This approach ensures effective, respectful, and empathetic communication, embodying a helpful and friendly demeanor.

Improve the following email by making it more professional, personalized, and effective. Maintain the original intent but enhance the structure, wording, and tone:
"""

# Function to improve email with OpenAI
def improve_email(email_text, model_name, api_key):
    """Generate improved email using OpenAI"""
    try:
        full_prompt = f"{EXECUTIVE_EDITOR_PROMPT}\n\n{email_text}"
        improved_email = openai_client.generate_with_openai(full_prompt, model_name)
        return improved_email
    except Exception as e:
        st.error(f"Error improving email: {e}")
        return None

# Main application
st.title("✉️ Professional Email Improver")
st.markdown("Transform your basic emails into professional, warm, and personalized communications")

# Sidebar for OpenAI API settings
st.sidebar.title("OpenAI API Settings")

# Get API key from environment variable or ask user
secret_value = os.getenv("OwadmasdujU")
if not secret_value:
    api_key = st.text_input("Enter your API key:", type="password")
else:
    api_key = secret_value

# Model selection
model_name = st.sidebar.selectbox(
    "Select OpenAI Model:", 
    ["gpt-4.1-nano", "gpt-4o-mini"],
    index=0
)

# Main content
st.header("Email Selection")

# Selection options: either pick a sample or write custom
input_option = st.radio(
    "Select an option:",
    ["Choose from sample emails", "Write your own email"]
)

email_text = ""

if input_option == "Choose from sample emails":
    # Sample email selection
    selected_question = st.selectbox(
        "Select a scenario:",
        list(SAMPLE_QUESTIONS_AND_EMAILS.keys())
    )
    
    email_text = SAMPLE_QUESTIONS_AND_EMAILS[selected_question]
    
    # Display the selected email
    st.subheader("Original Email")
    st.text_area("Original content:", email_text, height=150, key="original_sample", disabled=True)
    
else:
    # Custom email input
    st.subheader("Your Email")
    email_text = st.text_area(
        "Enter your email text:",
        "",
        height=150,
        key="custom_email"
    )

# Check conditions for improvement
has_email = email_text.strip() != ""
has_api_key = api_key is not None and api_key.strip() != ""

# Single button with conditions in the button callback
if st.button("Improve Email", key="improve_email_button"):
    if not has_email:
        st.warning("Please enter or select an email to improve")
    elif not has_api_key:
        st.warning("Please enter your OpenAI API key in the sidebar")
    else:
        with st.spinner("Enhancing your email..."):
            improved_email = improve_email(email_text, model_name, api_key)
            
            if improved_email:
                # Display results side by side
                st.header("Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Original Email")
                    st.text_area("", email_text, height=300, key="original_result", disabled=True)
                    
                with col2:
                    st.subheader("Improved Email")
                    st.text_area("", improved_email, height=300, key="improved_result")
                    
                # Add a download button for the improved email
                st.download_button(
                    "Download Improved Email",
                    improved_email,
                    "improved_email.txt",
                    "text/plain",
                    key='download-email'
                )
                
                # Add copy button (using JavaScript)
                st.markdown("""
                <div style="text-align: center; margin: 20px 0;">
                    <button onclick="navigator.clipboard.writeText(document.querySelector('.stTextArea[data-testid*=\"stTextArea\"]:nth-of-type(2) textarea').value)">
                        Copy to Clipboard
                    </button>
                </div>
                """, unsafe_allow_html=True)

# Tips for better emails
with st.expander("Tips for Professional Emails"):
    st.markdown("""
    ### 📧 Email Best Practices
    
    1. **Clear Subject Line**: Make it specific and relevant
    2. **Professional Greeting**: Address the recipient appropriately
    3. **Concise Content**: Keep your email brief and to the point
    4. **Professional Tone**: Maintain a respectful and positive tone
    5. **Proper Closing**: Include a professional sign-off
    6. **Proofread**: Check for spelling and grammar errors
    7. **Format Properly**: Use paragraphs and bullet points for readability
    8. **Response Time**: Acknowledge emails promptly, even if just to confirm receipt
    """)

# Footer
st.markdown("---")
st.markdown("✨ *Powered by OpenAI and the Executive Editor prompt* ✨") 