import streamlit as st
import json
import requests
import os

# Variables
model_name = os.getenv("OPENAI_MODEL")

#---------------- Header with API control --------------
pagename = "Search Normalization"
pageicon = "🔍"
st.set_page_config(page_title=pagename, layout="wide",page_icon=pageicon)
st.subheader(f"{pageicon} {pagename}")
with st.expander(f"Description of {pagename}", expanded=False):
    st.markdown("""
This tool helps you convert customer search queries into standardized automotive terminology. You can:

- Transform casual or slang terms into proper automotive part names
- Convert vehicle descriptions into structured data (year, make, model)
- Identify parts based on symptoms or vague descriptions
- Standardize search terms for better results in parts catalogs
- Improve search accuracy by normalizing common variations

Whether customers search using technical terms, common names, or symptoms, this tool helps ensure they find the exact parts they need.
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

# Function to call OpenAI API with model_name
def query_openai(prompt: str, api_key: str):
    # Create a detailed system prompt for accurate auto parts normalization
    system_prompt = """You are a search engine for auto parts. Take a search query and normalize it to a JSON object with the following fields:
    Output format: {"year": "1994", "make": "Honda", "model": "Civic", "part": "Piston Ring"}
    Try and infer what part the customer needs, even if given just a symptom or a vague description.
    Convert all slang and common terms to the correct part name."""
    
    # Status container to show information about the process
    status_container = st.container()
    
    with status_container:
        st.write("### Processing Steps")
        step1 = st.empty()
        step2 = st.empty()
        step3 = st.empty()
        
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
                "content": prompt
            }
        ],
        "response_format": {"type": "json_object"}
    }
    
    # Step 3: Making the API call
    with status_container:
        step3.warning("🔄 Sending to AI model...")
    
    try:
        # Direct API call without simulated delays
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
        st.error(f"Error calling OpenAI API: {str(e)}")
        return {"error": str(e)}, status_container

# Main app logic
st.write("""Enter a query like '94 Civic front end' or '88 e30 blue smoke' below to see how it gets converted into precise part information. This helps match customer descriptions to the correct parts, even when they use informal language or describe symptoms rather than parts.""")

# Example buttons
examples = [
    "2010 Camry squeelin",
    "F150 2015 blinker fluid",
    "2005 BMW 5 idle rough and stalling",
    "04 Vw Gulf Alt"
]

st.write("Example Queries:")
# Create horizontal layout for example buttons
cols = st.columns(len(examples))
for i, col in enumerate(cols):
    with col:
        if st.button(examples[i], key=f"example_{i}", use_container_width=True):
            st.session_state.search_query = examples[i]
            st.session_state.is_processing = True
            # Use st.rerun() instead of st.experimental_rerun()
            st.rerun()
        
# Search input
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
    
# Initialize session state for processing status
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False

search_query = st.text_input("Search for auto parts:", value=st.session_state.search_query, 
                             placeholder="Example: 94 Civic front end")

# Add a Go button instead of automatic processing
search_col, button_col = st.columns([5, 1])
with button_col:
    go_button = st.button("Go!", type="primary", use_container_width=True)

# Process when user clicks the Go button or an example button was clicked
if (go_button or st.session_state.is_processing) and search_query and api_key:
    # Call OpenAI API
    response, status_container = query_openai(search_query, api_key)
    
    # Display results
    if "error" in response:
        st.error(f"Error: {response['error']}")
    elif "choices" in response and len(response["choices"]) > 0:
        try:
            # Extract and parse the JSON response
            content = response["choices"][0]["message"]["content"]
            normalized_data = json.loads(content)
            
            # Show raw JSON output
            st.info(f"Raw JSON output: {content}")
            
            # Generate customer statement
            year = normalized_data.get("year", "")
            make = normalized_data.get("make", "")
            model = normalized_data.get("model", "")
            part = normalized_data.get("part", "")
            
            # Create the statement
            vehicle_info = ""
            if year:
                vehicle_info += year + " "
            if make:
                vehicle_info += make + " "
            if model:
                vehicle_info += model
            
            if vehicle_info and part:
                st.success(f"The customer is looking for a **{part}** for their **{vehicle_info.strip()}**.")
            elif part:
                st.success(f"The customer is looking for a **{part}**.")
            else:
                st.error("Unable to determine what the customer is looking for.")

            # Reset processing state for next search
            st.session_state.is_processing = False
            
        except json.JSONDecodeError:
            st.error("Failed to parse response as JSON")
            st.write("Raw response:", content)
            st.session_state.is_processing = False
    else:
        st.error("No response received from API")
        st.session_state.is_processing = False
elif search_query and not api_key and go_button:
    st.warning("Please enter your API key to process the search query.")
    st.session_state.is_processing = False
