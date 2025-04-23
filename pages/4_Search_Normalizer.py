import streamlit as st
import json
import requests
import time
import os

# Configure page settings
st.set_page_config(page_title="ACPN2025", layout="wide")

# Title and introduction
st.title("ACPN2025 Platform")
st.write("Welcome to the Auto Parts Search Normalizer.")

# Get API key from user input
secret_value = os.getenv("OwadmasdujU")
if not secret_value:
    api_key = st.text_input("Enter your API key:", type="password")
else:
    api_key = secret_value

# Function to call OpenAI API with GPT-4.1 Nano
def query_openai(prompt: str, api_key: str):
    """Send a prompt to OpenAI's GPT-4.1 Nano model and get a normalized auto part response"""
    
    # Create a detailed system prompt for accurate auto parts normalization
    system_prompt = """You are an automotive parts database expert. Your task is to normalize user search queries into standardized part information.

RULES:
1. Extract YEAR (4-digit when possible), MAKE, MODEL, and PART NAME from the query
2. Standardize part terminology according to auto industry conventions
3. Return ONLY a JSON object with these fields (no text, explanations, or reasoning)
4. If any field cannot be confidently determined, use null for that field
5. For common abbreviations, expand them (e.g., "civ" = "Civic", "alt" = "Altima")
6. Convert 2-digit years to 4-digit (e.g., "94" = "1994", "05" = "2005")
7. Normalize make/model capitalization (e.g., "honda civic" = "Honda Civic")
8. Recognize car part slang/alternatives (e.g., "front end" = "Front Bumper", "oil pan" = "Oil Pan")
9. If you have a hard time understanding the part name, think of context like "Noise Maker" being a horn or "Brake Stopper" being a brake pad.

Fields = year, make, model, part
"""
    
    # Status container to show information about the process
    status_container = st.container()
    
    with status_container:
        st.write("### Processing Steps")
        step1 = st.empty()
        step2 = st.empty()
        step3 = st.empty()
        
        # Step 1: Show the user's query
        step1.info(f"📝 Query recognized: '{prompt}'")
        time.sleep(0.5)  # Give user time to see this step
        
        # Step 2: Building request
        step2.info("🔧 Building API request with system instructions...")
        time.sleep(0.7)  # Give user time to see this step
    
    # Create the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-4.1-nano",
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
        step3.warning("🔄 Sending to AI model and awaiting response...")
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    # Make the API call and time it
    start_time = time.time()
    
    try:
        # Simulate API call progress (slower to give user more insight)
        for percent_complete in range(101):
            time.sleep(0.03)  # Longer delay to show progress more clearly
            progress_bar.progress(percent_complete)
            if percent_complete < 30:
                status_text.text("Analyzing automotive terms...")
            elif percent_complete < 60:
                status_text.text("Normalizing part terminology...")
            elif percent_complete < 90:
                status_text.text("Structuring JSON response...")
            else:
                status_text.text("Finalizing results...")
            
        # Actual API call
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        end_time = time.time()
        processing_time = round(end_time - start_time, 2)
        
        with status_container:
            status_text.text(f"✅ Complete in {processing_time} seconds!")
            step3.success("✅ Response received from AI model")
        
        return response.json(), processing_time, status_container
    
    except requests.exceptions.RequestException as e:
        with status_container:
            status_text.text("❌ Error during API call!")
            step3.error("❌ API call failed")
        st.error(f"Error calling OpenAI API: {str(e)}")
        return {"error": str(e)}, 0, status_container

# Main app logic
st.header("Auto Parts Search")
st.write("Enter a search query like '94 Civic front end' and see how it gets normalized.")
        
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

# Process when user clicks the Go button
if go_button and search_query and api_key:
    st.session_state.is_processing = True

if st.session_state.is_processing and search_query and api_key:
    # Call OpenAI API
    response, processing_time, status_container = query_openai(search_query, api_key)
    
    # Display results
    if "error" in response:
        st.error(f"Error: {response['error']}")
    elif "choices" in response and len(response["choices"]) > 0:
        try:
            # Extract and parse the JSON response
            content = response["choices"][0]["message"]["content"]
            normalized_data = json.loads(content)
            
            # Display normalized data in a nice format
            st.success("✨ Normalization successful!")
            
            # Create a table with the normalized data
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Normalized Result")
                data_table = {
                    "Field": ["Year", "Make", "Model", "Part"],
                    "Value": [
                        normalized_data.get("year", "N/A"),
                        normalized_data.get("make", "N/A"),
                        normalized_data.get("model", "N/A"),
                        normalized_data.get("part", "N/A")
                    ]
                }
                st.table(data_table)
            
            with col2:
                st.subheader("JSON Output")
                st.json(normalized_data)
            
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