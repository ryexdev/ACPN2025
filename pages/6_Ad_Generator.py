import streamlit as st
import json
import requests
import os
import io
import base64
from PIL import Image
import random

# API Key Control and model selection
secret_value = os.getenv("OwadmasdujU")
model_name = "gpt-4.1-nano"

#---------------- Header with API control --------------
pagename = "Automotive Ad Generator"
pageicon = "📃"
st.set_page_config(page_title=pagename, layout="wide",page_icon=pageicon)
st.subheader(f"{pageicon} {pagename}")
with st.expander(f"Description of {pagename}", expanded=False):
    st.markdown("""
Generate professional, platform-optimized social media ads for automotive parts and accessories. 
This tool uses AI to create engaging ad copy tailored to different social platforms (Instagram, LinkedIn, Facebook, etc.), 
target audiences, and marketing styles. The output includes customized ad text, suggested hashtags, and formatting 
specific to each platform's best practices.
""")
#API Key Control
if 'openai_api_key' not in st.session_state:
    st.session_state['openai_api_key'] = None
secret_value = os.getenv("OwadmasdujU")
if secret_value:
    st.success("OpenAI API key has been provided until EOD 5/14/2025")
    api_key = secret_value
    st.session_state['openai_api_key'] = secret_value
elif st.session_state['openai_api_key']:
    col1, col2 = st.columns([5, 1])
    with col1:
        st.success("Using user-provided OpenAI API key")
    with col2:
        if st.button("Clear Key", type="secondary", use_container_width=True):
            st.session_state['openai_api_key'] = None
            st.rerun()
    api_key = st.session_state['openai_api_key']
else:
    with st.container(border=True):
        st.warning("Please enter your [OpenAI API key](https://openai.com/api/).")
        api_key_input = st.text_input("Enter your API key:", type="password")
        if api_key_input:
            st.session_state['openai_api_key'] = api_key_input
        api_key = st.session_state['openai_api_key']

st.divider()
#-----------------------------------------------------------

# Custom CSS for better styling
st.markdown("""
<style>
    .ad-preview {
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .hashtags {
        color: #1DA1F2;
        font-weight: 500;
    }
    .platform-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #e1e8ed;
    }
    .platform-icon {
        width: 24px;
        height: 24px;
        margin-right: 10px;
    }
    .brand-name {
        font-weight: bold;
        font-size: 15px;
    }
    .instagram-post {
        border: 1px solid #e1e8ed;
        border-radius: 8px;
        overflow: hidden;
    }
    .facebook-post {
        border: 1px solid #dddfe2;
        border-radius: 8px;
        overflow: hidden;
    }
    .twitter-post {
        border: 1px solid #e1e8ed;
        border-radius: 12px;
        overflow: hidden;
    }
    .linkedin-post {
        border: 1px solid #e1e8ed;
        border-radius: 8px;
        overflow: hidden;
    }
    .tiktok-post {
        border: 1px solid #e1e8ed;
        border-radius: 8px;
        overflow: hidden;
        background-color: #010101;
        color: #ffffff;
    }
    .post-header {
        padding: 12px 16px;
        display: flex;
        align-items: center;
    }
    .profile-pic {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    .profile-info {
        flex: 1;
    }
    .username {
        font-weight: bold;
        margin-bottom: 2px;
    }
    .timestamp {
        font-size: 12px;
        color: #657786;
    }
    .post-content {
        padding: 0 16px 16px;
    }
    .post-text {
        margin: 12px 0;
        line-height: 1.4;
    }
    .post-actions {
        display: flex;
        padding: 0 16px 16px;
        color: #657786;
    }
    .action-button {
        margin-right: 20px;
        font-size: 14px;
    }
    .tiktok-content {
        background-color: #010101;
        color: white;
    }
    .tiktok-actions {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 15px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Example options for demonstration
options = [
    {"PartType":"Ignition Coil", "Brand": "Bosch", "Style": "Funny", "Platform": "Instagram", "Audience": "DIY Mechanics", "Max Length": 375},
    {"PartType":"Mass Air Flow Sensor", "Brand": "United Motor Products", "Style": "Funny", "Platform": "LinkedIn", "Audience": "Professional Mechanics", "Max Length": 275},
    {"PartType":"Oil Filter", "Brand": "Frame", "Style": "Funny", "Platform": "Facebook", "Audience": "General Public", "Max Length": 300},
    {"PartType":"Air Filter", "Brand": "Wix", "Style": "Funny", "Platform": "TikTok", "Audience": "Car Enthusiasts", "Max Length": 250},
    {"PartType":"Brake Pad", "Brand": "Perfect Stop", "Style": "Funny", "Platform": "LinkedIn", "Audience": "Educational", "Max Length": 350},
    {"PartType":"Brake Rotor", "Brand": "Winhere", "Style": "Funny", "Platform": "Twitter/X", "Audience": "DIY Mechanics", "Max Length": 275},
    {"PartType":"Brake Caliper", "Brand": "Cardone", "Style": "Funny", "Platform": "Facebook", "Audience": "General Public", "Max Length": 400},
    {"PartType":"Brake Line", "Brand": "Dorman", "Style": "Funny", "Platform": "TikTok", "Audience": "Car Enthusiasts", "Max Length": 450}
]

# Part information input
st.header("Ad Information")
st.write("This tool generates ad text for automotive parts and accessories. It uses AI to create engaging ad copy tailored to different social platforms (Instagram, LinkedIn, Facebook, etc.), target audiences, and marketing styles.")

# Add radio button to toggle between example mode and manual mode
input_mode = st.radio(
    "Select Input Mode",
    ["Use Examples", "Manual Input"],
    horizontal=True
)

col1, col2 = st.columns(2)
with col1:
    if input_mode == "Use Examples":
        part_type = st.selectbox("Automotive Part Type", options=[opt["PartType"] for opt in options], index=0)
        
        # Get matching brand options for selected part type
        matching_brands = [opt["Brand"] for opt in options if opt["PartType"] == part_type]
        brand = st.selectbox(f"Brand (auto selected for `{part_type}`)", options=matching_brands, index=0)
        
        # Get matching audience options for selected part type
        matching_audiences = [opt["Audience"] for opt in options if opt["PartType"] == part_type]
        target_audience = st.selectbox(f"Target Audience (auto selected for `{part_type}`)", options=matching_audiences)
    else:
        part_type = st.text_input("Automotive Part Type", "")
        brand = st.text_input("Brand (optional)", "")
        target_audience = st.selectbox(
            "Target Audience",
            ["DIY Mechanics", "Professional Mechanics", "General Public", "Car Enthusiasts", "Educational", "Business Owners"]
        )

with col2:
    if input_mode == "Use Examples":
        # Get matching style options for selected part type
        matching_styles = [opt["Style"] for opt in options if opt["PartType"] == part_type]
        ad_style = st.selectbox(f"Ad Style (auto selected for `{part_type}`)", options=matching_styles)
        
        # Get matching platform options for selected part type
        matching_platforms = [opt["Platform"] for opt in options if opt["PartType"] == part_type]
        platform = st.selectbox(f"Social Media Platform (auto selected for `{part_type}`)", options=matching_platforms)
        
        # Get default max length from selected option
        default_max_length = next((opt["Max Length"] for opt in options if opt["PartType"] == part_type and opt["Brand"] == brand), 300)
        max_length = st.slider(f"Maximum Ad Length (characters) (auto selected for `{part_type}`)", 50, 500, default_max_length)
    else:
        ad_style = st.selectbox(
            "Ad Style",
            ["Funny", "Informative", "Professional", "Engaging", "Technical", "Emotional"]
        )
        platform = st.selectbox(
            "Social Media Platform",
            ["Instagram", "LinkedIn", "Facebook", "Twitter/X", "TikTok"]
        )
        max_length = st.slider(f"Maximum Ad Length (characters) (auto selected for `{part_type}`)", 50, 500, 300)

# Advanced Options (collapsible)
with st.expander("Advanced Options"):
    st.subheader("Customize Prompt Templates")
    st.write("You can customize the prompt templates to generate ads that are more specific to your brand and audience.")
    
    # Default text prompt templates
    if 'text_system_prompt_template' not in st.session_state:
        st.session_state.text_system_prompt_template = """You are an expert automotive marketing specialist. 
Create an engaging social media ad for an automotive part that would perform well on the specified platform.
The ad should be in the specified style and targeted to the right audience.
Include appropriate hashtags that are relevant to automotive parts and the specific part type.
Separate the hashtags at the end with a double newline.
Do not include any image descriptions or placeholders."""
    
    if 'text_user_prompt_template' not in st.session_state:
        st.session_state.text_user_prompt_template = """Create a {style} social media ad for {part_type}{brand_text} to be posted on {platform}.
Target audience: {audience}
Maximum length: {max_length} characters (not including hashtags)

The ad should grab attention, convey value, and include a call to action.
End with 3-5 relevant hashtags separated by a double newline."""
    
    if 'image_prompt_template' not in st.session_state:
        st.session_state.image_prompt_template = """Create a professional, high-quality marketing image for a social media ad about {part_type} {platform_style}.
The image should complement this ad copy: "{ad_text}"

The image should be clean, modern, and visually appealing with good lighting and composition.
Style: Product photography with lifestyle elements, professional, high-resolution.
Do not include any text in the image."""
    
    # Text prompt customization
    st.markdown("#### Text Generation System Prompt")
    st.session_state.text_system_prompt_template = st.text_area(
        "System prompt template (instructions to AI)",
        st.session_state.text_system_prompt_template,
        height=150
    )
    
    st.markdown("#### Text Generation User Prompt")
    st.markdown("*Available variables: {style}, {part_type}, {brand_text}, {platform}, {audience}, {max_length}*")
    st.session_state.text_user_prompt_template = st.text_area(
        "User prompt template (specific request)",
        st.session_state.text_user_prompt_template,
        height=150
    )
    
    # Image prompt customization
    st.markdown("#### Image Generation Prompt")
    st.markdown("*Available variables: {part_type}, {platform_style}, {ad_text}*")
    st.session_state.image_prompt_template = st.text_area(
        "Image prompt template",
        st.session_state.image_prompt_template,
        height=150
    )
    
    # OpenAI model selection
    st.markdown("#### Model Settings")
    openai_model = st.selectbox(
        "OpenAI Model",
        options=model_name
    )
    os.environ['OPENAI_MODEL'] = openai_model
    
    image_quality = st.selectbox(
        "Image Quality",
        ["standard", "hd"],
        index=0
    )
    
    temperature = st.slider("Temperature (Creativity)", 0.0, 1.0, 0.7, 0.1)

# Function to generate ad text
def generate_ad_text(part_type, brand, ad_style, platform, target_audience, max_length):
    # Prepare system prompt
    system_prompt = st.session_state.text_system_prompt_template
    
    # Prepare user prompt with variables replaced
    brand_text = f" from {brand}" if brand else ""
    user_prompt = st.session_state.text_user_prompt_template.format(
        style=ad_style.lower(),
        part_type=part_type,
        brand_text=brand_text,
        platform=platform,
        audience=target_audience,
        max_length=max_length
    )
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": os.getenv('OPENAI_MODEL', model_name),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": st.session_state.get('temperature', 0.7)
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        ad_text = response.json()['choices'][0]['message']['content']
        
        # Split text and hashtags
        parts = ad_text.split('\n\n')
        if len(parts) > 1:
            main_text = parts[0]
            hashtags = parts[-1]
            return main_text, hashtags
        return ad_text, ""
    
    except Exception as e:
        st.error(f"Error generating ad text: {str(e)}")
        return None, None

# Function to render platform-specific UI
def render_platform_post(platform, brand, ad_text, hashtags):
    if platform == "Instagram":
        render_instagram_post(brand, ad_text, hashtags)
    elif platform == "Facebook":
        render_facebook_post(brand, ad_text, hashtags)
    elif platform == "Twitter/X":
        render_twitter_post(brand, ad_text, hashtags)
    elif platform == "LinkedIn":
        render_linkedin_post(brand, ad_text, hashtags)
    elif platform == "TikTok":
        render_tiktok_post(brand, ad_text, hashtags)

# Platform-specific post renderers
def render_instagram_post(brand, ad_text, hashtags):
    brand_name = brand if brand else "AutoPartsCo"
    
    st.markdown(f"""
    <div class="ad-preview instagram-post">
        <div class="post-header">
            <div class="profile-pic">
                <span style="font-size: 20px;">🚗</span>
            </div>
            <div class="profile-info">
                <div class="username">{brand_name}</div>
                <div class="timestamp">Sponsored</div>
            </div>
        </div>
        <div class="post-content">
            <div class="post-text">{ad_text}</div>
            <div class="hashtags">{hashtags}</div>
        </div>
        <div class="post-actions">
            <span class="action-button">❤️ Like</span>
            <span class="action-button">💬 Comment</span>
            <span class="action-button">📤 Share</span>
            <span class="action-button">🔖 Save</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_facebook_post(brand, ad_text, hashtags):
    brand_name = brand if brand else "AutoPartsCo"
    
    st.markdown(f"""
    <div class="ad-preview facebook-post">
        <div class="post-header">
            <div class="profile-pic">
                <span style="font-size: 20px;">🚗</span>
            </div>
            <div class="profile-info">
                <div class="username">{brand_name}</div>
                <div class="timestamp">Sponsored · <i class="fas fa-globe"></i></div>
            </div>
        </div>
        <div class="post-content">
            <div class="post-text">{ad_text}</div>
            <div class="hashtags">{hashtags}</div>
        </div>
        <div class="post-actions">
            <span class="action-button">👍 Like</span>
            <span class="action-button">💬 Comment</span>
            <span class="action-button">↗️ Share</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_twitter_post(brand, ad_text, hashtags):
    brand_name = brand if brand else "AutoPartsCo"
    username = brand_name.replace(" ", "")
    
    st.markdown(f"""
    <div class="ad-preview twitter-post">
        <div class="post-header">
            <div class="profile-pic">
                <span style="font-size: 20px;">🚗</span>
            </div>
            <div class="profile-info">
                <div class="username">{brand_name} <span style="color: #657786; font-weight: normal;">@{username.lower()}</span></div>
                <div class="timestamp">Promoted</div>
            </div>
        </div>
        <div class="post-content">
            <div class="post-text">{ad_text}</div>
            <div class="hashtags">{hashtags}</div>
        </div>
        <div class="post-actions">
            <span class="action-button">💬 Reply</span>
            <span class="action-button">🔄 Repost</span>
            <span class="action-button">❤️ Like</span>
            <span class="action-button">📊 View</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_linkedin_post(brand, ad_text, hashtags):
    brand_name = brand if brand else "AutoPartsCo"
    
    st.markdown(f"""
    <div class="ad-preview linkedin-post">
        <div class="post-header">
            <div class="profile-pic">
                <span style="font-size: 20px;">🚗</span>
            </div>
            <div class="profile-info">
                <div class="username">{brand_name}</div>
                <div class="timestamp">Promoted · Automotive</div>
            </div>
        </div>
        <div class="post-content">
            <div class="post-text">{ad_text}</div>
            <div class="hashtags">{hashtags}</div>
        </div>
        <div class="post-actions">
            <span class="action-button">👍 Like</span>
            <span class="action-button">💬 Comment</span>
            <span class="action-button">🔄 Repost</span>
            <span class="action-button">↗️ Send</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_tiktok_post(brand, ad_text, hashtags):
    brand_name = brand if brand else "AutoPartsCo"
    username = brand_name.replace(" ", "").lower()
    
    st.markdown(f"""
    <div class="ad-preview tiktok-post">
        <div class="post-header" style="color: white;">
            <div class="profile-pic">
                <span style="font-size: 20px;">🚗</span>
            </div>
            <div class="profile-info">
                <div class="username" style="color: white;">@{username}</div>
                <div class="timestamp" style="color: #aaa;">Sponsored</div>
            </div>
        </div>
        <div class="post-content tiktok-content">
            <div class="post-text">{ad_text}</div>
            <div class="hashtags">{hashtags}</div>
        </div>
        <div class="post-actions">
            <span class="action-button">❤️ {random.randint(1000, 99999)}</span>
            <span class="action-button">💬 {random.randint(100, 9999)}</span>
            <span class="action-button">🔄 {random.randint(100, 9999)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Generate button
if st.button("Generate Ad", type="primary", use_container_width=True):
    if not part_type:
        st.warning("Please enter a part type to generate an ad.")
    elif not api_key:
        st.warning("Please provide an OpenAI API key to generate the ad.")
    else:
        # Store temperature in session state
        st.session_state.temperature = st.session_state.get('temperature', 0.7)
        
        with st.spinner("Generating ad content..."):
            ad_text, hashtags = generate_ad_text(part_type, brand, ad_style, platform, target_audience, max_length)
            
            if ad_text:
                st.success("Ad text generated!")
                
                # Store important data in session state for potential reuse
                st.session_state.last_ad_text = ad_text
                st.session_state.last_hashtags = hashtags
                
                # Display the ad preview
                st.header("Ad Preview")
                
                preview_col1, preview_col2 = st.columns([3, 2])
                
                with preview_col1:
                    # Render platform-specific post UI
                    render_platform_post(platform, brand, ad_text, hashtags)
                
                with preview_col2:
                    st.subheader("Ad Details")
                    st.write(f"**Part Type:** {part_type}")
                    if brand:
                        st.write(f"**Brand:** {brand}")
                    st.write(f"**Style:** {ad_style}")
                    st.write(f"**Platform:** {platform}")
                    st.write(f"**Target Audience:** {target_audience}")
                    
                    # Export ad text
                    full_text = ad_text
                    if hashtags:
                        full_text += f"\n\n{hashtags}"
                    
                    st.download_button(
                        label="Download Ad Text",
                        data=full_text,
                        file_name="ad_text.txt",
                        mime="text/plain"
                    )
                
                # Collapsible sections for prompts and responses
                st.subheader("Generation Details")
                
                with st.expander("Text Generation Prompt & Response"):
                    st.markdown("### Text Generation Prompt")
                    st.code(f"System: {st.session_state.text_system_prompt_template}\n\nUser: {st.session_state.text_user_prompt_template}", language="markdown")
                    
                    st.markdown("### Text Generation Response")
                    st.code(f"Ad Text: {ad_text}\n\nHashtags: {hashtags}", language="markdown")
            else:
                st.error("Failed to generate ad text. Please try again.")

# Footer
st.markdown("---")
st.markdown("AI-powered ad generation for automotive parts marketing") 