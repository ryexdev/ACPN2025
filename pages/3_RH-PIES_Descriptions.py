import streamlit as st
import os
import pandas as pd
import time

from classes.utils.pies_prompt_builder import pies_prompt_builder
from classes.ai_engines.openai_client import openai_client
from classes.db import db

# Page configuration
st.set_page_config(
    page_title="PIES Description Builder",
    page_icon="🚗",
    layout="wide"
)

st.info("🤖💬 Generate PIES-compliant product descriptions for auto parts using AI (GPT-4.1-Nano)!")

# Database connection
def get_db_connection():
    in_docker = os.path.exists('/.dockerenv')
    if not db.connection_status():
        st.sidebar.error("❌ Failed to connect to database")
        return None
    st.sidebar.success("✅ Connected to database")
    return db.get_connection()

# Description generator
def generate_description(prompt, api_key=None):
    try:
        return openai_client.generate_with_openai(prompt, "gpt-4.1-nano")
    except Exception as e:
        st.error(f"Error generating description: {e}")
        return None

# In-page API key prompt (not in sidebar)
st.subheader("API Key Configuration")
secret_value = os.getenv("OwadmasdujU")
if not secret_value:
    api_key = st.text_input("Enter your API key:", type="password")
else:
    api_key = secret_value
    st.success("✅ API key loaded from environment")

# Part info entry
st.subheader("Part Information")
input_mode = st.radio("Select input mode:", ["Select from Database", "Enter Manually"])
product_info = {}

if input_mode == "Select from Database":
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT part_number, product_category, brand FROM parts LIMIT 100")
        parts = cursor.fetchall()

        if parts:
            parts_df = pd.DataFrame(parts)
            selected_part = st.selectbox(
                "Select Part Number:",
                parts_df["part_number"].tolist(),
                format_func=lambda x: f"{x} - {parts_df[parts_df['part_number'] == x]['product_category'].iloc[0]}"
            )
            cursor.execute("SELECT * FROM parts WHERE part_number = ?", (selected_part,))
            part_details = cursor.fetchone()

            if part_details:
                product_info = part_details
                st.subheader("Part Details")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Part Number:** {part_details['part_number']}")
                    st.write(f"**Product Category:** {part_details['product_category']}")
                with col2:
                    st.write(f"**Brand:** {part_details['brand']}")
                    st.write(f"**Part Type:** {part_details.get('part_type', 'N/A')}")
        else:
            st.warning("No parts found in database.")
            input_mode = "Enter Manually"
        cursor.close()
        conn.close()
    else:
        input_mode = "Enter Manually"

if input_mode == "Enter Manually":
    col1, col2 = st.columns(2)
    with col1:
        part_number = st.text_input("Part Number")
        product_category = st.text_input("Product Category (e.g., Ignition Coil)")
    with col2:
        brand = st.text_input("Brand")
        part_type = st.text_input("Part Type")

    with st.expander("Additional Attributes (Optional)"):
        col1, col2, col3 = st.columns(3)
        with col1:
            engine_application = st.text_input("Engine Application")
        with col2:
            material = st.text_input("Material")
        with col3:
            fitment = st.text_input("Fitment")

    product_info = {
        "part_number": part_number,
        "product_category": product_category,
        "brand": brand,
        "part_type": part_type,
        "engine_application": engine_application,
        "material": material,
        "fitment": fitment
    }

# Description config
st.subheader("Description Configuration")
desc_codes = pies_prompt_builder.get_pies_description_codes()
description_type = st.selectbox(
    "Select Description Type",
    list(desc_codes.keys()),
    format_func=lambda x: f"{x} - {desc_codes[x]}"
)

with st.expander("Advanced Options"):
    language_code = st.selectbox("Language Code", ["EN", "ES", "FR", "DE"], index=0)
    maintenance_type = st.selectbox("Maintenance Type", ["A", "D", "N"], index=0, format_func=lambda x: {
        "A": "A - Add or change", "D": "D - Delete", "N": "N - No change"}.get(x, x))
    sequence = st.number_input("Sequence", min_value=1, max_value=999, value=1)

# Generate button
st.subheader("Description Generation")
generate_clicked = st.button("Generate Description", key="generate_btn")

if generate_clicked:
    if product_info.get("product_category"):
        prompt = pies_prompt_builder.build_pies_prompt(product_info, description_type)
        with st.expander("View Prompt"):
            st.code(prompt)

        with st.spinner("Generating description..."):
            description = generate_description(prompt, api_key)
            if description:
                for char in pies_prompt_builder.invalid_characters:
                    description = description.replace(char, "")

                validation = pies_prompt_builder.validate_pies_description(description_type, description)
                st.subheader("Generated Description")
                edited = st.text_area("Edit if needed:", description, height=70)

                if edited != description:
                    description = edited
                    validation = pies_prompt_builder.validate_pies_description(description_type, edited)

                if not validation["is_valid"]:
                    st.warning("Validation Issues:")
                    for issue in validation["issues"]:
                        st.warning(f"• {issue}")
                else:
                    st.success("Description is valid according to PIES standards")

                st.subheader("XML Output")
                xml_output = (
                    f'<Descriptions>\n'
                    f'  <Description LanguageCode="{language_code}" '
                    f'MaintenanceType="{maintenance_type}" '
                    f'DescriptionCode="{description_type}" '
                    f'Sequence="{sequence}">{description}</Description>\n'
                    f'</Descriptions>'
                )
                st.code(xml_output, language="xml")

                col1, col2 = st.columns(2)
                with col1:
                    csv = pd.DataFrame([{
                        "LanguageCode": language_code,
                        "MaintenanceType": maintenance_type,
                        "DescriptionCode": description_type,
                        "Sequence": sequence,
                        "Description": description
                    }]).to_csv(index=False).encode("utf-8")
                    st.download_button("Export to CSV", csv, "pies_description.csv", "text/csv")
                with col2:
                    st.download_button("Export to XML", xml_output, "pies_description.xml", "application/xml")
    else:
        st.warning("Please provide product category info before generating a description.")
