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

# Page configuration
st.set_page_config(
    page_title="PIES Description Builder",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database connection function
def get_db_connection():
    """Create a connection to the MySQL database with multiple fallbacks using PyMySQL"""
    st.sidebar.markdown("### Database Connection")
    
    # Check if we're running inside Docker
    in_docker = os.path.exists('/.dockerenv')
    
    # Configure based on environment
    if in_docker:
        st.sidebar.text("Running inside Docker container")
        # In Docker, use the Docker service name
        configs = [
            {"host": "db", "port": 3306},
            {"host": "pies-desc-genie-db-1", "port": 3306},
        ]
    else:
        st.sidebar.text("Running on host machine")
        # On host machine, connect to the exposed port
        configs = [
            {"host": "localhost", "port": 3307},
            {"host": "127.0.0.1", "port": 3307}
        ]
    
    
    # Check if the database connection is successful
    if not db.connection_status():
        st.sidebar.error("❌ Failed to connect to database")
        return None
    else:
        st.sidebar.success("✅ Connected to database")
    
    return db.get_connection()

# Function to fetch available Ollama models
def get_ollama_models(ollama_url):
    """Fetch available models from Ollama server"""
    try:
        response = requests.get(f"{ollama_url}/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [model["name"] for model in models]
        return ["llama2"]  # Default fallback
    except Exception as e:
        st.warning(f"Could not fetch Ollama models: {e}")
        return ["llama2"]  # Default fallback

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

# Sidebar for model selection
st.sidebar.title("AI Model Selection")

model_source = st.sidebar.radio("Choose Model Source:", ["OpenAI", "Ollama"])

if model_source == "OpenAI":
    model_name = st.sidebar.selectbox("Select OpenAI Model:", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"])
    
    # Get API key from user input
    secret_value = os.getenv("OwadmasdujU")
    if not secret_value:
        api_key = st.sidebar.text_input("Enter OpenAI API Key:", type="password")
    else:
        api_key = st.sidebar.text_input("Enter OpenAI API Key:", type="password", value=secret_value)
    
    # Set API key for this request
    os.environ["OPENAI_API_KEY"] = api_key
else:
    ollama_url = st.sidebar.text_input("Ollama Server URL", value=os.getenv("OLLAMA_URL", "http://localhost:11434"))
    
    # Fetch Ollama models button
    if st.sidebar.button("Fetch Ollama Models"):
        ollama_models = get_ollama_models(ollama_url)
        st.session_state["ollama_models"] = ollama_models
    
    # Use cached models or defaults
    ollama_models = st.session_state.get("ollama_models", ["llama2", "mistral", "phi3"])
    model_name = st.sidebar.selectbox("Select Ollama Model:", ollama_models)

# Main application
st.title("PIES Description Builder")
st.markdown("Generate Auto Care PIES-compliant product descriptions using AI")

# Part Selection Section
st.header("Part Information")

# Option to select from database or enter manually
input_mode = st.radio("Select input mode:", ["Select from Database", "Enter Manually"])

product_info = {}

if input_mode == "Select from Database":
    # Connect to database and fetch part numbers
    conn = get_db_connection()
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
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Part Number:** {part_details['part_number']}")
                    st.write(f"**Product Category:** {part_details['product_category']}")
                with col2:
                    st.write(f"**Brand:** {part_details['brand']}")
                    st.write(f"**Part Type:** {part_details.get('part_type', 'N/A')}")
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
        product_category = st.text_input("Product Category (e.g., Ignition Coil, Oxygen Sensor)")
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

# Description Configuration
st.header("Description Configuration")

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
        ["EN", "ES", "FR", "DE"],
        index=0
    )
    maintenance_type = st.selectbox(
        "Maintenance Type", 
        ["A", "D", "N"],
        index=0,
        format_func=lambda x: {
            "A": "A - Add or change",
            "D": "D - Delete",
            "N": "N - No change"
        }.get(x, x)
    )
    sequence = st.number_input("Sequence", min_value=1, max_value=999, value=1)

# Description generation and display
st.header("Description Generation")

generate_button = st.button("Generate Description")

if generate_button and product_info.get("product_category"):
    # Build prompt from product info
    prompt = pies_prompt_builder.build_pies_prompt(product_info, description_type)
    
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
        st.session_state.descriptions = []
        st.experimental_rerun() 