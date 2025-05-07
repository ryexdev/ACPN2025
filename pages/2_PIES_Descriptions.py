import streamlit as st
import os
import json
import pandas as pd
import requests

# Import utility functions
from classes.utils.pies_prompt_builder import pies_prompt_builder
from classes.ai_engines.openai_client import openai_client
from classes.ai_engines.ollama_client import ollama_client
from classes.db import db

# Ollama API key (Check README.md for more information)
secret_value = os.getenv("OwadmasdujU")
model_source = "OpenAI"
model_name = "gpt-4.1-nano"

# Disable Ollama option for the demo
# Look at the README.md file for more information
ollama_inactive = True


# Page configuration
st.set_page_config(
    page_title="PIES Description Builder",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to generate PIES description
def generate_description(prompt, model_source, model_name, api_key=None, ollama_url=None):
    """Generate description using selected AI model"""
    try:
        if model_source == 'OpenAI':
            # API key is already set in the sidebar
            return openai_client.generate_with_openai(prompt, model_name)
        elif model_source == 'Ollama':
            # Override URL for this request
            os.environ["OLLAMA_URL"] = ollama_url
            return ollama_client.generate_with_ollama(prompt, model_name)
    except Exception as e:
        st.error(f"Error generating description: {e}")
        return None


# Main application
st.title("📑 PIES Description Builder")
with st.expander("Description of PIES Description Builder", expanded=True):
    st.markdown(f"""
    This tool helps you generate professional product descriptions that comply with Auto Care PIES (Product Information Exchange Standard) requirements using AI technology.

    You can:
    - Connect to either OpenAI or Ollama language models { "<i>(Ollama deactivated for demo)</i>" if ollama_inactive else "OpenAI" }
    - Select parts from an existing database or enter new part details manually  
    - Generate accurate, standardized descriptions for automotive parts and components
    - Save generated descriptions for future reference

    The AI models are specifically tuned to create consistent, detailed product descriptions following PIES formatting guidelines and automotive industry best practices.
    """, unsafe_allow_html=True)

if not secret_value:
    with st.container(border=True):
        st.subheader("OpenAI API Key")
        st.warning("API key is not set. Please enter your API key below to continue to use the tool.")
        api_key = st.text_input("Enter your API key:", type="password")
else:
    st.success("OpenAI API key has been provided for the demo. You can freely use the tool until the API key expires (estimated 2025-05-14 @ 12:00 MST).")
    api_key = secret_value

if not ollama_inactive:
    with st.expander("LLM Connection Configuration"):
        st.write("This section allows you to configure the connection to the LLM (Large Language Model). You can choose between OpenAI and Ollama as your LLM provider. If you choose OpenAI, you need to provide your API key. If you choose Ollama, you need to provide the URL of the Ollama server.")
        
        model_source = st.radio("Choose Model Source:", ["OpenAI", "Ollama"])

        if model_source == "OpenAI":
            model_name = st.selectbox("Select OpenAI Model:", ["gpt-4.1-nano", "gpt-4o-mini"])
            
        else:
            st.warning("Ollama integration is currently not configured for this demo. Please use OpenAI.")
            ollama_url = st.text_input("Ollama Server URL", value=os.getenv("OLLAMA_URL", "http://localhost:11434"), disabled=ollama_inactive)
            
            # Fetch Ollama models button
            if st.button("Fetch Ollama Models", disabled=ollama_inactive):
                ollama_models = ollama_client.get_ollama_models(ollama_url)
                st.session_state["ollama_models"] = ollama_models
            
            # Use cached models or defaults
            ollama_models = st.session_state.get("ollama_models", ["llama2", "mistral", "phi3"])
            model_name = st.selectbox("Select Ollama Model:", ollama_models, disabled=ollama_inactive)

colBody1, colBody2 = st.columns([1,3])
with colBody1:
    # Part Selection Section
    st.header("Part Information")
    st.write("Please select the part information from the database or enter the information manually.")
    with st.container(border=True):

        # Option to select from database or enter manually
        input_mode = st.radio("Select input mode:", ["Select from Database", "Enter Manually"])

        product_info = {}

        if input_mode == "Select from Database":
            # Connect to database and fetch part numbers
            conn = db.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT part_number, product_category, brand FROM parts LIMIT 100")
                parts = cursor.fetchall()
                
                if parts:
                    # Create a selection dataframe
                    parts_df = pd.DataFrame(parts)
                    selected_part = st.selectbox(
                        "Select Part Number:", 
                        parts_df["part_number"].tolist(),
                        format_func=lambda x: f"{x} - {parts_df[parts_df['part_number']==x]['product_category'].iloc[0]}"
                    )
                    
                    # Fetch detailed part information
                    cursor.execute(
                        "SELECT * FROM parts WHERE part_number = ?", 
                        (selected_part,)
                    )
                    part_details = cursor.fetchone()
                    
                    if part_details:
                        product_info = part_details
                        
                        # Display part details
                        st.subheader("Part Details")
                        
                        # Create data for table
                        data = {
                            "Field": ["Part Number", "Product Category", "Brand", "Part Type"],
                            "Value": [
                                part_details['part_number'],
                                part_details['product_category'], 
                                part_details['brand'],
                                part_details.get('part_type', 'N/A')
                            ]
                        }
                        
                        # Convert to DataFrame and display as table
                        df = pd.DataFrame(data)
                        # Create a more key-value style table by not transposing
                        st.table(df.set_index('Field').style.set_properties(**{'width': '75%'}))
                else:
                    st.warning("No parts found in database. Please enter part information manually.")
                    input_mode = "Enter Manually"
                
                cursor.close()
                conn.close()
            else:
                st.warning("Could not connect to database. Please enter part information manually.")
                input_mode = "Enter Manually"

        if input_mode == "Enter Manually":
            col1, col2 = st.columns(2)
            with col1:
                part_number = st.text_input("Part Number")
                product_category = st.text_input("Category (e.g. Oxygen Sensor)")
            with col2:
                brand = st.text_input("Brand")
                part_type = st.text_input("Part Type")
            
            # Additional attributes
            st.subheader("Additional Attributes (Optional)")
            col1, col2, col3 = st.columns(3)
            with col1:
                engine_application = st.text_input("Engine Application")
            with col2:
                material = st.text_input("Material")
            with col3:
                fitment = st.text_input("Fitment")
            
            # Store manually entered info
            product_info = {
                "part_number": part_number,
                "product_category": product_category,
                "brand": brand,
                "part_type": part_type,
                "engine_application": engine_application,
                "material": material,
                "fitment": fitment
            }


with colBody2:
    # Description Configuration
    st.header("Description Configuration")
    st.write("""Please select the description type and advanced options below.The description type determines the format and purpose of the generated content. Advanced options allow you to customize the language code, maintenance type, and sequence.""")
    
    with st.container(border=True):
        # Description type selection
        desc_codes = pies_prompt_builder.get_pies_description_codes()
        description_type = st.selectbox(
            "Select Description Type", 
            list(desc_codes.keys()),
            format_func=lambda x: f"{x} - {desc_codes[x]}"
        )

        # Advanced options (collapsible)
        with st.expander("Advanced Options"):
            language_code = st.selectbox(
                "Language Code", 
                ["ENGL", "SPAN", "FREN", "GERM"],
                index=0
            )
            maintenance_type = st.selectbox(
                "Maintenance Type", 
                ["ADD", "DEL", "NOC"],
                index=0,
                format_func=lambda x: {
                    "ADD": "A - Add or Update",
                    "DEL": "D - Delete",
                    "NOC": "N - No Change"
                }.get(x, x)
            )
            sequence = st.number_input("Sequence", min_value=1, max_value=999, value=1)


st.divider()

# Description generation and display
st.header("Description Generation")
st.write("""Please click the button below to generate the description. The description will be displayed in the text area below. You can edit the description if needed. Once you are happy with the description, you can click the button to save the description to the database.""")

generate_button = st.button("Generate Description")

if generate_button and product_info.get("product_category"):
    # Build prompt from product info
    prompt = pies_prompt_builder.build_pies_prompt(product_info, description_type, language_code)
    
    # Show the prompt (collapsible)
    with st.expander("View Prompt"):
        st.code(prompt)
    
    # Generate description with selected model
    with st.spinner("Generating description..."):
        if model_source == "OpenAI":
            description = generate_description(
                prompt, model_source, model_name, api_key
            )
        else:
            description = generate_description(
                prompt, model_source, model_name, ollama_url=ollama_url
            )

        # Remove invalid characters
        for char in pies_prompt_builder.invalid_characters:
            description = description.replace(char, "")
        
        if description:
            # Store in session state
            if "descriptions" not in st.session_state:
                st.session_state.descriptions = []
            
            # Add to descriptions list
            st.session_state.descriptions.append({
                "LanguageCode": language_code,
                "MaintenanceType": maintenance_type,
                "DescriptionCode": description_type,
                "Sequence": sequence,
                "Description": description
            })
            
            # Validation
            validation = pies_prompt_builder.validate_pies_description(description_type, description)
            
            # Show description with editable text area
            st.subheader("Generated Description")
            edited_description = st.text_area(
                "Edit if needed:", 
                description, 
                height=150
            )
            
            # Update the description in session state if edited
            if edited_description != description:
                st.session_state.descriptions[-1]["Description"] = edited_description
                
                # Re-validate after edit
                validation = pies_prompt_builder.validate_pies_description(description_type, edited_description)
            
            # Show validation results
            if not validation["is_valid"]:
                st.warning("Validation Issues:")
                for issue in validation["issues"]:
                    st.warning(f"• {issue}")
            else:
                st.success("Description is valid according to PIES standards")
else:
    if generate_button:
        st.warning("Please provide product category information before generating a description.")

# Show all generated descriptions
if "descriptions" in st.session_state and st.session_state.descriptions:
    st.header("Generated Descriptions")
    
    # Create a DataFrame for display
    descriptions_df = pd.DataFrame(st.session_state.descriptions)
    st.dataframe(descriptions_df)
    
    # XML Output
    st.subheader("XML Output")
    
    xml_output = "<Descriptions>\n"
    for desc in st.session_state.descriptions:
        xml_output += f'  <Description LanguageCode="{desc["LanguageCode"]}" '
        xml_output += f'MaintenanceType="{desc["MaintenanceType"]}" '
        xml_output += f'DescriptionCode="{desc["DescriptionCode"]}" '
        xml_output += f'Sequence="{desc["Sequence"]}">'
        xml_output += f'{desc["Description"]}</Description>\n'
    xml_output += "</Descriptions>"
    
    st.code(xml_output, language="xml")
    
    # Add export buttons
    col1, col2 = st.columns(2)
    with col1:
        # Export to CSV
        csv = descriptions_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Export to CSV",
            csv,
            "pies_descriptions.csv",
            "text/csv",
            key='csv-download'
        )
    
    with col2:
        # Export to XML
        st.download_button(
            "Export to XML",
            xml_output,
            "pies_descriptions.xml",
            "application/xml",
            key='xml-download'
        )
    
    # Clear button
    if st.button("Clear All Descriptions"):
        if "descriptions" in st.session_state:
            del st.session_state.descriptions
        st.rerun()