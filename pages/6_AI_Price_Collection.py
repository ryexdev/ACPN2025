import streamlit as st
from openai import OpenAI
import os
import json

# Set up the page configuration
st.set_page_config(page_title="Auto Parts Price Scraper", page_icon="🔍")

# Title and description
st.title("AI Price Collection")
st.markdown("Collect prices for auto parts across multiple retailers using AI")

# Get API key from environment variable or ask user
open_ai_api_key = os.getenv("OwadmasdujU")

def search_openai_for_price(part_number, retailer_site, part_type):
    # Create a container for logs
    log_container = st.expander("API Request and Response Logs", expanded=False)
    
    # Log the steps and parameters
    with log_container:
        st.write("### Step 1: Setting up parameters")
        st.write(f"Part Number: {part_number}")
        st.write(f"Retailer Site: {retailer_site}")
        
        # Create a search query specifically formatted for part price search
        search_query = f"Can you search google.com to find the price of the {part_number} {part_type} for the site of {retailer_site}."
        st.write(f"Search Query: {search_query}")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=open_ai_api_key)
    
    try:
        with log_container:
            st.write("### Step 2: Making the request to OpenAI using responses API")
        
        # Using the responses API with web_search_preview tool
        response = client.responses.create(
            model="gpt-4o",
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "You are a helpful assistant that finds prices of auto parts. Your goal is use google.com to find the price of the part number and part_type on the site of the retailer."
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"Can you search google.com to find the price of the {part_number} {part_type} on site:{retailer_site}. Return the part number, brand, price, and a link to the product."
                        }
                    ]
                }
            ],
            text={
                "format": {
                    "type": "text"
                }
            },
            tools=[
                {
                    "type": "web_search_preview",
                    "search_context_size": "high"
                }
            ],
            temperature=0,
            max_output_tokens=2048
        )
        
        # Log the response
        with log_container:
            st.write("### Step 3: API Response Received")
            
            # Safely extract and display the response content
            if response and hasattr(response, 'output'):
                st.write("Response Output:")
                for output_item in response.output:
                    if output_item.type == 'web_search_call':
                        st.write("Web search was performed")
                    elif output_item.type == 'message':
                        if hasattr(output_item, 'content'):
                            for content_item in output_item.content:
                                if content_item.type == 'text':
                                    st.write(f"Content: {content_item.text}")
                                elif content_item.type == 'annotations':
                                    st.write("Annotations found:")
                                    for annotation in content_item.annotations:
                                        if annotation.type == 'url_citation':
                                            st.write(f"URL cited: {annotation.url}")
            
            # Display the full output text if available
            if hasattr(response, 'output_text'):
                st.write("### Complete Response Text:")
                st.write(response.output_text)
            
        # Return the output text or a default message
        return response.output_text if hasattr(response, 'output_text') else "Could not retrieve price information"
    
    except Exception as e:
        with log_container:
            st.error(f"### Error in API Call: {str(e)}")
            st.error(f"Full error details: {repr(e)}")
        return f"Error: {str(e)}"

# Create a form for user input
with st.form(key="search_form"):
    # Input for part number
    part_number = st.text_input("Enter Part Number", placeholder="Example: 22A")
    part_type = st.text_input("Enter Part Type", placeholder="Example: Wiper Blade")
    
    # Dropdown for store selection
    store_options = [
        "AutoZone",
        "Advanced Auto Parts",
        "O'Reillys", 
        "Napa",
        "RockAuto"
    ]
    selected_store = st.selectbox("Select Retailer", options=store_options)
    
    # Search button
    search_button = st.form_submit_button("Search")

    if search_button:
        if part_number and selected_store and part_type:
            if selected_store == "AutoZone":
                retailer_site = "autozone.com"
            elif selected_store == "Advanced Auto Parts":
                retailer_site = "advancedautoparts.com"
            elif selected_store == "O'Reillys":
                retailer_site = "oreillyauto.com"
            elif selected_store == "Napa":
                retailer_site = "napaonline.com"
            elif selected_store == "RockAuto":
                retailer_site = "rockauto.com"

            # Show searching notification
            with st.spinner(''):
                search_status = st.success("🔍 Searching for price information...")
                
                # Get price information
                price = search_openai_for_price(part_number, retailer_site, part_type)
                
                # Remove the searching notification
                search_status.empty()
                
                # Show the results
                st.write("### Results:")
                st.success(price)

