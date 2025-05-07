import streamlit as st
from openai import OpenAI
import os

# Get API key from environment variable
# secret_value = None
secret_value = os.getenv("OwadmasdujU")
model_name = "gpt-4o"

# Set up the page configuration
st.set_page_config(
    page_title="AI Price Collection", 
    page_icon="💵",
    layout="wide"
)

# Title and description
st.title("💵 AI Price Collection")
with st.expander("Description of AI Price Collection", expanded=True):
    st.markdown("""
    This tool helps you collect and compare prices for automotive parts across multiple online retailers using AI technology. You can:

    - Search for specific part numbers across major auto parts retailers
    - Get real-time price comparisons from different websites
    - View detailed product information including availability and shipping options
    - Track price history and identify the best deals
    - Export price data for analysis and reporting

    The AI-powered search ensures accurate price matching and helps you find the best deals for your automotive parts needs.
    """)

# Get API key from environment variable or ask user
if not secret_value:
    with st.container(border=True):
        st.subheader("OpenAI API Key")
        st.warning("API key is not set. Please enter your API key below to continue to use the tool.")
        secret_value = st.text_input("Enter your OpenAI API key", type="password")
        # Model selection
        model_name = st.selectbox(
            "Select OpenAI Model (selected model required for the tool to work):", 
            ["gpt-4o"],
            index=0,
            disabled=True
        )
else:
    st.success("OpenAI API key has been provided for the demo. You can freely use the tool until the API key expires (estimated 2025-05-14 @ 12:00 MST).")
    open_ai_api_key = secret_value


def search_openai_for_price(part_number, retailer_site, part_type):
    # Create a container for logs
    log_container = st.expander("API Request and Response Logs", expanded=False)
    
    # Log the steps and parameters
    with log_container:
        st.write("### Step 1: Setting up parameters")
        st.write(f"Part Number: `{part_number}`")
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
            model=model_name,
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

# Product Options
product_options = [
    {"store_name": "AutoZone", "retailer_site": "autozone.com", "part_type": "Wiper Blade", "part_number": "22A"},
    {"store_name": "Advanced Auto Parts", "retailer_site": "advancedautoparts.com", "part_type": "Wiper Blade", "part_number": "22A"},
    {"store_name": "Carparts", "retailer_site": "carparts.com", "part_type": "Wiper Blade", "part_number": "22A"},
    {"store_name": "O'Reillys", "retailer_site": "oreillyauto.com", "part_type": "Wiper Blade", "part_number": "22A"},
    {"store_name": "Napa", "retailer_site": "napaonline.com", "part_type": "Wiper Blade", "part_number": "22A"},
    {"store_name": "RockAuto", "retailer_site": "rockauto.com", "part_type": "Wiper Blade", "part_number": "22A"},

    {"store_name": "Advanced Auto Parts", "retailer_site": "advancedautoparts.com", "part_type": "Brake Caliper", "part_number": "18-B4729"},
    {"store_name": "AutoZone", "retailer_site": "autozone.com", "part_type": "Brake Caliper", "part_number": "18-B4729"},
    {"store_name": "O'Reillys", "retailer_site": "oreillyauto.com", "part_type": "Brake Caliper", "part_number": "18-B4729"},
    {"store_name": "Carparts", "retailer_site": "carparts.com", "part_type": "Brake Caliper", "part_number": "18-B4729"},
    {"store_name": "Napa", "retailer_site": "napaonline.com", "part_type": "Brake Caliper", "part_number": "18-B4729"},
    {"store_name": "RockAuto", "retailer_site": "rockauto.com", "part_type": "Brake Caliper", "part_number": "18-B4729"},

    {"store_name": "Advanced Auto Parts", "retailer_site": "advancedautoparts.com", "part_type": "Air Suspension", "part_number": "949-852"},
    {"store_name": "AutoZone", "retailer_site": "autozone.com", "part_type": "Air Suspension", "part_number": "949-852"},
    {"store_name": "O'Reillys", "retailer_site": "oreillyauto.com", "part_type": "Air Suspension", "part_number": "949-852"},
    {"store_name": "Carparts", "retailer_site": "carparts.com", "part_type": "Air Suspension", "part_number": "949-852"},
    {"store_name": "Napa", "retailer_site": "napaonline.com", "part_type": "Air Suspension", "part_number": "949-852"},
    {"store_name": "RockAuto", "retailer_site": "rockauto.com", "part_type": "Air Suspension", "part_number": "949-852"},

    {"store_name": "AutoZone", "retailer_site": "autozone.com", "part_type": "Oil Filter", "part_number": "S8A"},
    {"store_name": "O'Reillys", "retailer_site": "oreillyauto.com", "part_type": "Air Filter", "part_number": "49250"},
    {"store_name": "Carparts", "retailer_site": "carparts.com", "part_type": "Brake Pads", "part_number": "TXH1308"},
    {"store_name": "RockAuto", "retailer_site": "rockauto.com", "part_type": "Oil Filter", "part_number": "51515"},
    {"store_name": "Napa", "retailer_site": "napaonline.com", "part_type": "Oil Filter", "part_number": "7356"},
    {"store_name": "RockAuto", "retailer_site": "rockauto.com", "part_type": "Ignition Coil", "part_number": "FD503"} 
]

# Initialize session state variables if they don't exist
if 'part_number' not in st.session_state:
    st.session_state.part_number = None
if 'part_type' not in st.session_state:
    st.session_state.part_type = None
if 'selected_store' not in st.session_state:
    st.session_state.selected_store = None
if 'reset_values' not in st.session_state:
    st.session_state.reset_values = False
if 'input_mode' not in st.session_state:
    st.session_state.input_mode = 'demo'

# Callback for part number change
def on_part_number_change():
    # Get the selected part number
    selected_part_number = st.session_state.part_number_select
    
    # Reset part type and store selection when part number changes
    st.session_state.part_number = selected_part_number
    st.session_state.part_type = None
    st.session_state.selected_store = None
    st.session_state.reset_values = True
    
# Callback for part type change
def on_part_type_change():
    # Get the selected part type
    selected_part_type = st.session_state.part_type_select
    
    # Update part type in session state and reset store selection
    st.session_state.part_type = selected_part_type
    st.session_state.selected_store = None

# Callback for input mode change
def on_input_mode_change():
    # Reset values when switching between demo and manual modes
    st.session_state.part_number = None
    st.session_state.part_type = None
    st.session_state.selected_store = None
    st.session_state.reset_values = True

col1, col2 = st.columns([1,3])
with col1:
    # Radio button for selecting between demo data and manual entry
    input_mode = st.radio(
        "Select Input Mode",
        options=["Use Demo Data", "Enter Part Details Manually"],
        index=0 if st.session_state.input_mode == 'demo' else 1,
        key="input_mode_radio",
        on_change=on_input_mode_change
    )
    
    # Update session state
    st.session_state.input_mode = 'demo' if input_mode == "Use Demo Data" else 'manual'
    
    if st.session_state.input_mode == 'demo':
        # Demo mode - select from predefined options
        # Get unique part numbers to avoid duplicates in the dropdown
        unique_part_numbers = list(set(option["part_number"] for option in product_options))
        
        # Outside the form, select part number
        part_number = st.selectbox(
            "Select Part Number", 
            options=unique_part_numbers, 
            key="part_number_select",
            on_change=on_part_number_change
        )

        # Get valid part types for the selected part number
        valid_part_types = list(set(option["part_type"] for option in product_options if option["part_number"] == part_number))
        if valid_part_types:
            # Set default part type if needed
            if st.session_state.reset_values or st.session_state.part_type not in valid_part_types:
                st.session_state.part_type = valid_part_types[0]
                st.session_state.reset_values = False
            
            # Select part type
            part_type = st.selectbox(
                f"Select Part Type (auto filled for `{part_number}`)", 
                options=valid_part_types, 
                index=valid_part_types.index(st.session_state.part_type) if st.session_state.part_type in valid_part_types else 0,
                key="part_type_select",
                on_change=on_part_type_change
            )
            
            # Get valid retailers for the selected part number and part type
            valid_retailers = list(set(option["store_name"] for option in product_options 
                                    if option["part_number"] == part_number and option["part_type"] == part_type))
            
            if valid_retailers:
                # Set default retailer if needed
                if st.session_state.selected_store not in valid_retailers:
                    st.session_state.selected_store = valid_retailers[0]
                
                # Select retailer
                selected_store = st.selectbox(
                    f"Select Retailer (selection filtered for `{part_number}`)", 
                    options=valid_retailers,
                    index=valid_retailers.index(st.session_state.selected_store) if st.session_state.selected_store in valid_retailers else 0,
                    key="retailer_select"
                )
                
                # Update session state
                st.session_state.selected_store = selected_store
            else:
                st.warning("No retailers available for the selected part number and part type.")
                selected_store = None
        else:
            st.warning("No part types available for the selected part number.")
            part_type = None
            selected_store = None
    else:
        # Manual entry mode
        part_number = st.text_input("Enter Part Number", key="manual_part_number")
        part_type = st.text_input("Enter Part Type", key="manual_part_type")
        
        # Predefined list of retailers for manual mode
        retailers = ["AutoZone", "Advanced Auto Parts", "O'Reillys", "Carparts", "Napa", "RockAuto"]
        selected_store = st.selectbox("Select Retailer", options=retailers, key="manual_retailer_select")
        
        # Get retailer site based on the selected store
        retailer_site_mapping = {
            "AutoZone": "autozone.com",
            "Advanced Auto Parts": "advancedautoparts.com",
            "O'Reillys": "oreillyauto.com",
            "Carparts": "carparts.com",
            "Napa": "napaonline.com",
            "RockAuto": "rockauto.com"
        }

# Search button
if st.button("Search", key="search_button"):
    if part_number and selected_store and part_type:
        if st.session_state.input_mode == 'demo':
            # Get retailer site based on selected options from demo data
            filtered_retailer_site = next((option["retailer_site"] for option in product_options 
                                        if option["part_number"] == part_number 
                                        and option["part_type"] == part_type 
                                        and option["store_name"] == selected_store), "")
        else:
            # Get retailer site from the mapping for manual mode
            retailer_site_mapping = {
                "AutoZone": "autozone.com",
                "Advanced Auto Parts": "advancedautoparts.com",
                "O'Reillys": "oreillyauto.com",
                "Carparts": "carparts.com",
                "Napa": "napaonline.com",
                "RockAuto": "rockauto.com"
            }
            filtered_retailer_site = retailer_site_mapping.get(selected_store, "")
        
        if filtered_retailer_site:
            # Show searching notification
            with st.spinner(''):
                search_status = st.success("🔍 Searching for price information...")
                
                # Get price information
                price = search_openai_for_price(part_number, filtered_retailer_site, part_type)
                
                # Remove the searching notification
                search_status.empty()
                
                # Show the results
                st.write("### Results:")
                st.success(price)
        else:
            st.error("Could not find retailer site for the selected options.")
    else:
        st.error("Please fill in all required fields: Part Number, Part Type, and Retailer.")

