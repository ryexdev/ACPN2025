import streamlit as st
import json
import requests
import os

# Variables
model_name = os.getenv("OPENAI_MODEL")

#---------------- Header with API control --------------
pagename = "Marketing Copy"
pageicon = "📑"
st.set_page_config(page_title=pagename, layout="wide",page_icon=pageicon)
st.subheader(f"{pageicon} {pagename}")
with st.expander(f"Description of {pagename}", expanded=False):
    st.markdown("""
This tool transforms raw supplier descriptions of auto parts into clear, customer-friendly **marketing copy**. It uses AI to convert technical or unstructured product data into standardized, engaging content that improves online catalog quality. You can:

- Automatically generate titles, descriptions, fitment notes, and feature lists
- Standardize terminology and highlight compatibility with specific vehicles
- Improve readability and SEO value of product listings
- Clearly communicate features, specifications, and benefits to customers
- Ensure important fitment details are preserved (e.g., drivetrain, bolt pattern)

Paste in a supplier-provided description and click **Rewrite Description** to instantly produce professional content ready for eCommerce.
""")
#API Key Control
if 'openai_api_key' not in st.session_state:
    st.session_state['openai_api_key'] = None
secret_value = os.getenv("OwadmasdujU")
if secret_value:
    st.success("OpenAI API key has been provided for free use.")
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
        st.warning("Please enter your [OpenAI API key](https://platform.openai.com/api-key). Tutorial: [How to get your OpenAI API key](https://www.youtube.com/watch?v=SzPE_AE0eEo)")
        api_key_input = st.text_input("Enter your API key:", type="password")
        if api_key_input:
            st.session_state['openai_api_key'] = api_key_input
        api_key = st.session_state['openai_api_key']
        
st.divider()
#-----------------------------------------------------------


# Pre-populated sample descriptions
default_description = """FRONT WHEEL HUB AND BEARING ASSEMBLY
- Compatible w/ 2017-2019 Ford Escape, Lincoln MKC
- Premium quality
- Heavy duty construction
- 5-lug bolt pattern
- Precise fitment
- Pre-lubricated with premium synthetic grease
- Includes sensor ring for ABS function
- Replacement for OE #AB123456
- Fits 4WD models only, will not fit 2WD
- Hub bore diameter: 65mm
- Bolt pattern: 5x108mm
- 4-bolt mount to steering knuckle
- 45mm thickness
- Made to OE specs
- Direct bolt-on
- Similar to ASM-512321, PDQ4321"""

# Text area for raw supplier description
st.write("""The text area below contains a sample automotive part description from a supplier. You can modify this or add your own product description, then click 'Rewrite Description' to generate clear, standardized marketing copy that highlights key product attributes and fitment details.""")

raw_description = st.text_area("Raw Supplier Description", 
                       value=default_description,
                       height=100)


# Function to call API for description rewriting
def rewrite_description(raw_text: str, api_key: str):    
    # Create a system prompt for description rewriting
    system_prompt = f"""You are an automotive parts description expert specializing in creating standardized marketing copy. Transform the raw supplier description into clear, professional, concise, marketing copy.
    
    JSON format for your response:
    "title": "Product title in clear, concise format",
    "description": "The main marketing description",
    "compatibility": "Clear statement of vehicle compatibility",
    "specifications": [List of key specifications in standardized format],
    "features_benefits": [List of key features and their benefits to the customer],
    "fitment_notes": "Any important notes about installation or fitment
    
    Make sure all important notes are included in the response.
    """
    
    # Status container to show information about the process
    status_container = st.container()
    
    with status_container:
        st.write("### Processing Steps")
        step1 = st.empty()
        step2 = st.empty()
        step3 = st.empty()
        
        # Step 1: Processing raw description
        step1.success("✅ Received raw product description")
        
        # Step 2: Building request
        step2.info("🔧 Building API request...")
    
    # Create the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system", 
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"Rewrite this automotive part description into standardized marketing copy:\n\n{raw_text}"
            }
        ],
        "response_format": {"type": "json_object"}
    }
    
    # Step 3: Making the API call
    with status_container:
        step3.warning("🔄 Sending to AI model...")
    
    try:
        # Direct API call
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()
        
        with status_container:
            step3.success("✅ Response received")
        
        return response.json(), status_container
    
    except requests.exceptions.RequestException as e:
        with status_container:
            step3.error("❌ API call failed")
        st.error(f"Error calling API: {str(e)}")
        return {"error": str(e)}, status_container

# Go button
go_button = st.button("Rewrite Description", type="primary")

# Process when user clicks the Go button
if go_button and api_key and raw_description:
    # Call API
    response, status_container = rewrite_description(raw_description, api_key)
    
    # Display formatted results
    if "error" in response:
        st.error(f"Error: {response['error']}")
    elif "choices" in response and len(response["choices"]) > 0:
        try:
            # Extract and parse the JSON response
            content = response["choices"][0]["message"]["content"]
            rewritten_data = json.loads(content)
            
            # Title
            if "title" in rewritten_data:
                st.markdown(f"## {rewritten_data['title']}")
            
            # Main description
            if "description" in rewritten_data:
                st.markdown(rewritten_data['description'])
            
            # Compatibility
            if "compatibility" in rewritten_data:
                st.markdown("### Compatibility")
                st.markdown(rewritten_data['compatibility'])
            
            # Specifications
            if "specifications" in rewritten_data and rewritten_data['specifications']:
                st.markdown("### Specifications")
                for spec in rewritten_data['specifications']:
                    st.markdown(f"- {spec}")
            
            # Features and benefits
            if "features_benefits" in rewritten_data and rewritten_data['features_benefits']:
                st.markdown("### Features & Benefits")
                for feature in rewritten_data['features_benefits']:
                    st.markdown(f"- {feature}")
            
            # Fitment notes
            if "fitment_notes" in rewritten_data and rewritten_data['fitment_notes']:
                st.markdown("### Fitment Notes")
                st.markdown(rewritten_data['fitment_notes'])
            
        except json.JSONDecodeError:
            st.error("Failed to parse response as JSON")
            st.text(content)
    else:
        st.error("No response received from API")
elif go_button and not api_key:
    st.warning("Please enter your API key to rewrite the description.")