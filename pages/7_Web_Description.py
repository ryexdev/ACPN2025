import streamlit as st
import json
import requests
import os

#---------------- Header with API control --------------
pagename = "Web Description"
pageicon = "🌐"
st.set_page_config(page_title=pagename, layout="wide",page_icon=pageicon)
st.subheader(f"{pageicon} {pagename}")
with st.expander(f"Description of {pagename}", expanded=False):
    st.markdown("""
This tool demonstrates how AI can be used in multiple successive steps to transform basic part information into comprehensive, customer-ready content. The tool follows these steps:

1. **Basic Normalization** - Convert casual or incomplete descriptions into standardized automotive terminology
2. **Technical Enhancement** - Add technical details, specifications, and compatibility information
3. **Marketing Polishing** - Transform technical information into customer-friendly marketing copy
4. **SEO Optimization** - Add relevant keywords and structure to improve search visibility

This iterative approach shows how AI can be used not just once, but in a strategic sequence to progressively refine content, saving hours of manual work while improving quality and consistency across your catalog.
""")

secret_value = os.getenv("OwadmasdujU")
if not secret_value:
    with st.container(border=True):
        st.warning("Please enter your [OpenAI API key](https://openai.com/api/).")
        api_key = st.text_input("Enter your API key:", type="password")
else:
    st.success("OpenAI API key has been provided until EOD 5/14/2025")
    api_key = secret_value
st.divider()
#-----------------------------------------------------------

# Function to call OpenAI API
def call_openai_api(prompt, system_prompt, api_key, step_name, status_placeholder):
    """General function to call OpenAI API with proper error handling"""
    
    # Update status
    status_placeholder.warning(f"🔄 Processing: {step_name}...")
    
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
    
    try:
        # Direct API call
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        
        # Extract content from response
        content = response.json()["choices"][0]["message"]["content"]
        result = json.loads(content)
        
        # Update status
        status_placeholder.success(f"✅ Completed: {step_name}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        status_placeholder.error(f"❌ Error in {step_name}")
        st.error(f"API Error: {str(e)}")
        return {"error": str(e)}
    except json.JSONDecodeError:
        status_placeholder.error(f"❌ Error parsing response in {step_name}")
        st.error("Failed to parse API response as JSON")
        return {"error": "JSON parsing error"}

# Step 1: Basic Normalization
def normalize_part_info(raw_input, api_key, status_placeholder):
    system_prompt = """You are an automotive parts normalization system. Convert the given raw part description into structured, standardized format.
    
    JSON format:
    {
        "part_name": "Standardized part name",
        "part_category": "Brake/Engine/Suspension/etc.",
        "vehicle_compatibility": "Extracted vehicle make/model/year information",
        "normalized_description": "A brief normalized description of the part"
    }
    
    Standardize terminology, extract vehicle compatibility information, and categorize the part correctly.
    """
    
    return call_openai_api(
        prompt=f"Normalize this automotive part description:\n\n{raw_input}",
        system_prompt=system_prompt,
        api_key=api_key,
        step_name="Basic Normalization",
        status_placeholder=status_placeholder
    )

# Step 2: Technical Enhancement
def enhance_technical_details(normalized_data, api_key, status_placeholder):
    # Convert normalized_data to string for prompt
    normalized_str = json.dumps(normalized_data, indent=2)
    
    system_prompt = """You are an automotive technical expert. Add detailed technical specifications and compatibility information to this normalized part data.
    
    JSON format:
    {
        "part_name": "Keep from input",
        "part_category": "Keep from input",
        "vehicle_compatibility": "Expanded vehicle compatibility list",
        "technical_specifications": {
            "dimensions": "Key dimensions with units",
            "material": "Material information",
            "oem_references": "OEM part numbers this replaces",
            "additional_specs": "Any other key technical specifications"
        },
        "installation_notes": "Technical notes about installation requirements",
        "normalized_description": "Keep from input"
    }
    
    Add realistic technical details based on the part category and vehicle compatibility.
    """
    
    return call_openai_api(
        prompt=f"Enhance these technical details for this automotive part:\n\n{normalized_str}",
        system_prompt=system_prompt,
        api_key=api_key,
        step_name="Technical Enhancement",
        status_placeholder=status_placeholder
    )

# Step 3: Marketing Polish
def create_marketing_copy(technical_data, api_key, status_placeholder):
    # Convert technical_data to string for prompt
    technical_str = json.dumps(technical_data, indent=2)
    
    system_prompt = """You are an automotive marketing expert. Transform this technical part data into compelling marketing copy.
    
    JSON format:
    {
        "product_title": "SEO-friendly product title with key features",
        "marketing_description": "Customer-friendly marketing description highlighting benefits",
        "key_features": ["List of customer benefits and key selling points"],
        "compatibility_statement": "Concise, clear vehicle compatibility statement",
        "warranty_info": "Any recommended warranty information",
        "technical_specifications": "Keep from input",
        "part_name": "Keep from input",
        "part_category": "Keep from input",
        "vehicle_compatibility": "Keep from input"
    }
    
    Focus on benefits to the customer, reliability, ease of installation, and value.
    """
    
    return call_openai_api(
        prompt=f"Create marketing copy for this automotive part:\n\n{technical_str}",
        system_prompt=system_prompt,
        api_key=api_key,
        step_name="Marketing Polish",
        status_placeholder=status_placeholder
    )

# Step 4: SEO Optimization
def optimize_for_seo(marketing_data, api_key, status_placeholder):
    # Convert marketing_data to string for prompt
    marketing_str = json.dumps(marketing_data, indent=2)
    
    system_prompt = """You are an e-commerce SEO specialist for automotive parts. Optimize this marketing content for search engines.
    
    JSON format:
    {
        "seo_optimized_title": "SEO-optimized product title (max 60 chars)",
        "meta_description": "SEO-friendly meta description (max 155 chars)",
        "primary_keywords": ["List of 5-7 primary keywords"],
        "long_tail_keywords": ["List of 3-5 longer search phrases"],
        "product_description_html": "HTML-formatted product description with proper heading structure",
        "product_structured_data": "JSON-LD schema markup for this product",
        "original_content": "Keep all fields from the input"
    }
    
    Ensure keywords are naturally incorporated in both title and description.
    """
    
    return call_openai_api(
        prompt=f"Optimize this automotive part content for SEO:\n\n{marketing_str}",
        system_prompt=system_prompt,
        api_key=api_key,
        step_name="SEO Optimization",
        status_placeholder=status_placeholder
    )

# Sample default input
default_input = """2012 Camry front pads - worn out after only 6 months use. Looking for better quality. Customer says there's squeaking.
Front brake application. Prefer ceramic."""

# User input
st.write("""Enter a basic part description below (as a customer or employee might initially describe it) and see how AI can progressively enhance it through multiple iterations. Each step builds on the previous one, demonstrating how AI can be used strategically in sequence.""")

user_input = st.text_area("Basic Part Description:", 
                       value=default_input,
                       height=100)

# Set up the layout with tabs for each step
tab_col1, tab_col2 = st.columns([4, 1])
with tab_col2:
    run_button = st.button("Process All Steps", type="primary", use_container_width=True)

if run_button and api_key and user_input:
    # Initialize status display
    progress_container = st.container()
    with progress_container:
        st.subheader("Processing Status")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            step1_status = st.empty()
        with col2:
            step2_status = st.empty()
        with col3:
            step3_status = st.empty()
        with col4:
            step4_status = st.empty()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Original Input", "Step 1: Normalization", "Step 2: Technical Details", "Step 3: Marketing Copy", "Step 4: SEO Optimization"])
    
    with tab1:
        st.text_area("Original Input", value=user_input, height=200, disabled=True)
    
    # Run Step 1
    normalized_result = normalize_part_info(user_input, api_key, step1_status)
    with tab2:
        st.json(normalized_result)
    
    # Run Step 2
    if "error" not in normalized_result:
        technical_result = enhance_technical_details(normalized_result, api_key, step2_status)
        with tab3:
            st.json(technical_result)
    else:
        step2_status.error("❌ Skipped due to previous error")
        technical_result = {"error": "Skipped due to previous error"}
    
    # Run Step 3
    if "error" not in technical_result:
        marketing_result = create_marketing_copy(technical_result, api_key, step3_status)
        with tab4:
            st.json(marketing_result)
    else:
        step3_status.error("❌ Skipped due to previous error")
        marketing_result = {"error": "Skipped due to previous error"}
    
    # Run Step 4
    if "error" not in marketing_result:
        seo_result = optimize_for_seo(marketing_result, api_key, step4_status)
        with tab5:
            # Show JSON
            with st.expander("Show Raw SEO Data", expanded=False):
                st.json(seo_result)
            
            # Show rendered product page preview
            if "seo_optimized_title" in seo_result and "product_description_html" in seo_result:
                st.subheader("Product Page Preview")
                st.markdown(f"# {seo_result['seo_optimized_title']}")
                st.markdown(seo_result['product_description_html'], unsafe_allow_html=True)
                
                # Keywords section
                if "primary_keywords" in seo_result:
                    st.subheader("SEO Keywords")
                    st.markdown("**Primary Keywords:**")
                    st.markdown(", ".join(seo_result["primary_keywords"]))
                    
                    if "long_tail_keywords" in seo_result:
                        st.markdown("**Long-tail Keywords:**")
                        st.markdown(", ".join(seo_result["long_tail_keywords"]))
                
                # Meta description
                if "meta_description" in seo_result:
                    st.subheader("Meta Description Preview")
                    st.markdown(f"*{seo_result['meta_description']}*")
    else:
        step4_status.error("❌ Skipped due to previous error")
        
    # Final summary
    st.subheader("AI Enhancement Process Complete")
    st.markdown("""
    The demonstration above shows how AI can be used in succession to progressively enhance automotive parts content:
    
    1. **Normalization**: Converting unstructured input into standardized terminology
    2. **Technical Enhancement**: Adding detailed specifications and compatibility data
    3. **Marketing Copy**: Transforming technical information into customer-friendly content
    4. **SEO Optimization**: Making the content search-engine friendly and discoverable
    
    This sequential AI approach can help automotive parts retailers save time, improve catalog consistency, and create better customer experiences.
    """)
    
elif run_button and not api_key:
    st.warning("Please enter your API key to process the description.")