import streamlit as st
import json
import requests
import time
import os

# Configure page settings
st.set_page_config(page_title="ACPN 2025", layout="wide")

st.info("🤖💬 Normalize slang and common terms for cars and parts, help funnel the customer to the right part!")

# Get API key from user input
secret_value = os.getenv("OwadmasdujU")
if not secret_value:
    api_key = st.text_input("Enter your API key:", type="password")
else:
    api_key = secret_value

# Function to call OpenAI API with GPT-4.1 Nano
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
        step3.warning("🔄 Sending to AI model...")
    
    try:
        # Direct API call without simulated delays
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
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
st.write("""Enter a search query like '94 Civic front end' or '88 e30 blue smoke' and see how it gets normalized. 

This can help customers who are searching for parts but may not know the exact terminology.""")
        
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
