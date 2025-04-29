import streamlit as st
import json
import requests
import os
import io
import base64
from PIL import Image
import random

# Configure page settings
st.set_page_config(
    page_title="Automotive Ad Generator",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .ad-preview {
        padding: 20px;
        border-radius: 10px;
        /*background-color: #f0f2f0;*/
        margin: 20px 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .hashtags {
        color: #1DA1F2;
        font-weight: 500;
    }
    .ad-image {
        max-width: 100%;
        border-radius: 8px;
        margin: 15px 0;
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
        /*background-color: #f3f6f8;*/
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
        /*background-color: #e1e8ed;*/
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
    .preview-image {
        max-height: 350px;
        width: auto;
        max-width: 100%;
        margin: 0 auto;
        display: block;
    }
    .image-container {
        text-align: center;
        position: relative;
    }
    .image-expand {
        position: absolute;
        bottom: 10px;
        right: 10px;
        background: rgba(0,0,0,0.5);
        color: white;
        border-radius: 4px;
        padding: 5px 10px;
        font-size: 12px;
        cursor: pointer;
        z-index: 100;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.title("Automotive Ad Generator")
st.markdown("Create engaging social media ads for automotive parts using AI")

# Get API key from environment variable or ask user
api_key = os.getenv("OwadmasdujU")
if not api_key:
    api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")

# Part information input
st.header("Ad Information")

col1, col2 = st.columns(2)
with col1:
    part_type = st.text_input("Automotive Part Type", placeholder="e.g., Ignition Coil, Mass Air Flow Sensor")
    brand = st.text_input("Brand (optional)", placeholder="e.g., ACDelco, Bosch")
    target_audience = st.selectbox(
        "Target Audience",
        ["DIY Mechanics", "Professional Mechanics", "Car Enthusiasts", "General Public"]
    )

with col2:
    ad_style = st.selectbox(
        "Ad Style",
        ["Funny", "Technical", "Educational", "Promotional", "Problem-Solution"]
    )
    platform = st.selectbox(
        "Social Media Platform",
        ["Instagram", "Facebook", "Twitter/X", "LinkedIn", "TikTok"]
    )
    max_length = st.slider("Maximum Ad Length (characters)", 50, 500, 275)

# Advanced Options (collapsible)
with st.expander("Advanced Options"):
    st.subheader("Customize Prompt Templates")
    
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
        ["gpt-4.1-nano", "gpt-4o-mini", "gpt-3.5-turbo"],
        index=1
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
        "model": os.getenv('OPENAI_MODEL', "gpt-4.1-nano"),
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

# Function to generate image based on ad text
def generate_image(ad_text, part_type, platform):
    platform_style = ""
    if platform == "Instagram":
        platform_style = "styled for Instagram with clean, bright aesthetics"
    elif platform == "Facebook":
        platform_style = "styled for Facebook with engaging, shareable visuals"
    elif platform == "Twitter/X":
        platform_style = "styled for Twitter with clear, attention-grabbing imagery"
    elif platform == "LinkedIn":
        platform_style = "styled for LinkedIn with professional, business-appropriate imagery"
    elif platform == "TikTok":
        platform_style = "styled for TikTok with vibrant, trendy visuals that appeal to younger audiences"
    
    # Use the custom image prompt template with variables replaced
    image_prompt = st.session_state.image_prompt_template.format(
        part_type=part_type,
        platform_style=platform_style,
        ad_text=ad_text
    )
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "dall-e-3",
        "prompt": image_prompt,
        "size": "1024x1024",
        "quality": st.session_state.get('image_quality', 'standard'),
        "n": 1
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        image_url = response.json()['data'][0]['url']
        
        # Get the image data
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        
        return image_response.content
    
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None

# Function to render platform-specific UI
def render_platform_post(platform, brand, ad_text, hashtags, image_data):
    if platform == "Instagram":
        render_instagram_post(brand, ad_text, hashtags, image_data)
    elif platform == "Facebook":
        render_facebook_post(brand, ad_text, hashtags, image_data)
    elif platform == "Twitter/X":
        render_twitter_post(brand, ad_text, hashtags, image_data)
    elif platform == "LinkedIn":
        render_linkedin_post(brand, ad_text, hashtags, image_data)
    elif platform == "TikTok":
        render_tiktok_post(brand, ad_text, hashtags, image_data)

# Platform-specific post renderers
def render_instagram_post(brand, ad_text, hashtags, image_data):
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
    """, unsafe_allow_html=True)
    
    # Display the image if available with controlled size
    if image_data:
        # Create a unique key for this session
        if 'image_counter' not in st.session_state:
            st.session_state.image_counter = 0
        else:
            st.session_state.image_counter += 1
        
        # Display smaller image in the preview
        image = Image.open(io.BytesIO(image_data))
        
        # Create a container with relative positioning for the expand button
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        
        # Show the image with controlled height (without key parameter)
        st.image(image, use_container_width=False, clamp=True, output_format="PNG", 
                 width=min(550, image.width))
        
        # Close the container
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
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

def render_facebook_post(brand, ad_text, hashtags, image_data):
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
    """, unsafe_allow_html=True)
    
    # Display the image if available with controlled size
    if image_data:
        # Display smaller image in the preview
        image = Image.open(io.BytesIO(image_data))
        
        # Create a container with relative positioning for the expand button
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        
        # Show the image with controlled height (without key parameter)
        st.image(image, use_container_width=False, clamp=True, output_format="PNG", 
                 width=min(550, image.width))
        
        # Close the container
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
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

def render_twitter_post(brand, ad_text, hashtags, image_data):
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
    """, unsafe_allow_html=True)
    
    # Display the image if available with controlled size
    if image_data:
        # Display smaller image in the preview
        image = Image.open(io.BytesIO(image_data))
        
        # Create a container with relative positioning for the expand button
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        
        # Show the image with controlled height (without key parameter)
        st.image(image, use_container_width=False, clamp=True, output_format="PNG", 
                 width=min(500, image.width))
        
        # Close the container
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
        </div>
        <div class="post-actions">
            <span class="action-button">💬 Reply</span>
            <span class="action-button">🔄 Repost</span>
            <span class="action-button">❤️ Like</span>
            <span class="action-button">📊 View</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_linkedin_post(brand, ad_text, hashtags, image_data):
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
    """, unsafe_allow_html=True)
    
    # Display the image if available with controlled size
    if image_data:
        # Display smaller image in the preview
        image = Image.open(io.BytesIO(image_data))
        
        # Create a container with relative positioning for the expand button
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        
        # Show the image with controlled height (without key parameter)
        st.image(image, use_container_width=False, clamp=True, output_format="PNG", 
                 width=min(500, image.width))
        
        # Close the container
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
        </div>
        <div class="post-actions">
            <span class="action-button">👍 Like</span>
            <span class="action-button">💬 Comment</span>
            <span class="action-button">🔄 Repost</span>
            <span class="action-button">↗️ Send</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_tiktok_post(brand, ad_text, hashtags, image_data):
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
    """, unsafe_allow_html=True)
    
    # Display the image if available with controlled size
    if image_data:
        # Display smaller image in the preview
        image = Image.open(io.BytesIO(image_data))
        
        # Create a container with relative positioning for the expand button
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        
        # Show the image with controlled height - TikTok is more vertical (without key parameter)
        st.image(image, use_container_width=False, clamp=True, output_format="PNG", 
                 width=min(400, image.width))
        
        # Close the container
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
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

# Store the enhanced download options in a function to avoid duplication and scope issues
def display_download_options(image_data, ad_text, hashtags):
    st.subheader("Download Options")
    
    # Image download
    if image_data:
        # Encode image to base64 for download
        img_bytes = io.BytesIO(image_data)
        b64 = base64.b64encode(img_bytes.getvalue()).decode()
        
        # Create a download link for the full-size image
        st.markdown(f"""
        <a href="data:image/png;base64,{b64}" download="ad_image.png" style="display: inline-block; padding: 0.5em 1em; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; margin-bottom: 15px;">
            <span style="vertical-align: middle;">⬇️ Download Full Size Image</span>
        </a>
        """, unsafe_allow_html=True)
        
        # Provide image dimensions info
        image = Image.open(io.BytesIO(image_data))
        st.caption(f"Full image dimensions: {image.width} x {image.height} px")
    
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

# Generate button
if st.button("Generate Ad", type="primary", use_container_width=True):
    if not part_type:
        st.warning("Please enter a part type to generate an ad.")
    elif not api_key:
        st.warning("Please provide an OpenAI API key to generate the ad.")
    else:
        # Store temperature and image quality in session state
        st.session_state.temperature = st.session_state.get('temperature', 0.7)
        st.session_state.image_quality = st.session_state.get('image_quality', 'standard')
        
        with st.spinner("Generating ad content..."):
            ad_text, hashtags = generate_ad_text(part_type, brand, ad_style, platform, target_audience, max_length)
            
            if ad_text:
                st.success("Ad text generated!")
                
                # Generate image based on ad text and platform
                with st.spinner("Creating matching image..."):
                    image_data = generate_image(ad_text, part_type, platform)
                
                if image_data:
                    # Store important data in session state for potential reuse
                    st.session_state.last_ad_text = ad_text
                    st.session_state.last_hashtags = hashtags
                    st.session_state.last_image_data = image_data
                    
                    # Display the ad preview
                    st.header("Ad Preview")
                    
                    preview_col1, preview_col2 = st.columns([3, 2])
                    
                    with preview_col1:
                        # Render platform-specific post UI
                        render_platform_post(platform, brand, ad_text, hashtags, image_data)
                    
                    with preview_col2:
                        st.subheader("Ad Details")
                        st.write(f"**Part Type:** {part_type}")
                        if brand:
                            st.write(f"**Brand:** {brand}")
                        st.write(f"**Style:** {ad_style}")
                        st.write(f"**Platform:** {platform}")
                        st.write(f"**Target Audience:** {target_audience}")
                        
                        # Display enhanced download options
                        display_download_options(image_data, ad_text, hashtags)
                    
                    # Collapsible sections for prompts and responses
                    st.subheader("Generation Details")
                    
                    with st.expander("Text Generation Prompt & Response"):
                        st.markdown("### Text Generation Prompt")
                        st.code(f"System: {st.session_state.text_system_prompt_template}\n\nUser: {st.session_state.text_user_prompt_template}", language="markdown")
                        
                        st.markdown("### Text Generation Response")
                        st.code(f"Ad Text: {ad_text}\n\nHashtags: {hashtags}", language="markdown")
                    
                    # Store the complete image prompt
                    platform_style = ""
                    if platform == "Instagram":
                        platform_style = "styled for Instagram with clean, bright aesthetics"
                    elif platform == "Facebook":
                        platform_style = "styled for Facebook with engaging, shareable visuals"
                    elif platform == "Twitter/X":
                        platform_style = "styled for Twitter with clear, attention-grabbing imagery"
                    elif platform == "LinkedIn":
                        platform_style = "styled for LinkedIn with professional, business-appropriate imagery"
                    elif platform == "TikTok":
                        platform_style = "styled for TikTok with vibrant, trendy visuals that appeal to younger audiences"
                    
                    image_prompt = st.session_state.image_prompt_template.format(
                        part_type=part_type,
                        platform_style=platform_style,
                        ad_text=ad_text
                    )
                    
                    with st.expander("Image Generation Prompt"):
                        st.markdown("### Image Generation Prompt")
                        st.code(image_prompt, language="markdown")
                else:
                    st.error("Failed to generate image. Please try again.")
            else:
                st.error("Failed to generate ad text. Please try again.")

# Footer
st.markdown("---")
st.markdown("AI-powered ad generation for automotive parts marketing") 