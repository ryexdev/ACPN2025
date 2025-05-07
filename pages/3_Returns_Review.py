import streamlit as st
import json
import requests
import os

#---------------- Header with API control --------------
pagename = "Returns Review"
pageicon = "🛠"
st.set_page_config(page_title=pagename, layout="wide",page_icon=pageicon)
st.subheader(f"{pageicon} {pagename}")
with st.expander(f"Description of {pagename}", expanded=False):
    st.markdown("""
This tool helps identify potential **fitment or compatibility issues** in customer product reviews for automotive parts. It leverages AI to extract and summarize recurring problems related to part compatibility by analyzing unstructured review text. You can:

- Detect patterns of installation or fitment issues tied to specific vehicle year/make/model/submodel
- Identify misleading catalog data (e.g., parts listed as compatible but consistently reported as not fitting)
- Support catalog correction and improve part listings
- Understand which submodels (e.g., SE vs. Titanium) are affected
- View confidence levels based on how frequently a problem is mentioned

Just paste or edit a set of customer reviews, and click **Analyze Reviews** to generate an AI-powered summary of key issues and affected vehicles.
""")
#API Key Control
if 'openai_api_key' not in st.session_state:
    st.session_state['openai_api_key'] = None
secret_value = os.getenv("OwadmasdujU")
if secret_value:
    st.success("OpenAI API key has been provided until EOD 5/14/2025")
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
        st.warning("Please enter your [OpenAI API key](https://openai.com/api/).")
        api_key_input = st.text_input("Enter your API key:", type="password")
        if api_key_input:
            st.session_state['openai_api_key'] = api_key_input
        api_key = st.session_state['openai_api_key']
        
st.divider()
#-----------------------------------------------------------


# Pre-populated reviews in a single text block
default_reviews = """Great quality hub assembly for my 2018 Ford Escape. Easy installation and perfect fit.
I bought this for my 2018 Ford Escape SE and it's been working well for about 2 months now. No issues with installation.
Not happy with this purchase. I have a 2019 Ford Escape and despite the listing saying it fits, the bolt pattern is slightly off. Had to return.
Worked perfectly on my 2018 Ford Escape Titanium. Make sure you have the right tools though!
This hub is good quality but doesn't fit my 2019 Ford Escape as advertised. The bolt holes don't line up correctly.
I installed this on my wife's 2017 Ford Escape without any problems. Great replacement part.
Perfect OEM replacement for my 2018 Ford Escape. Would buy again.
The description said it fits 2019 Ford Escape but the bolt pattern is wrong. Wasted time trying to make it work.
I'm a mechanic and installed this on a customer's 2018 Ford Escape. Perfect fit and function.
Decent quality but fitment issues with my 2019 Ford Escape. Had to modify slightly to make it work.
Works great on my 2018 Ford Escape. Easy install and quieted down the wheel bearing noise completely.
This is the second one I've ordered for different vehicles. First one was perfect for my 2018 Escape, but this one doesn't fit my 2019 Escape properly.
Installed on my 2018 Ford Kuga (European model) with no issues at all. Perfect replacement part.
Great part for my 2018 Ford C-Max. Exact fit and quieted the bearing noise.
Bought for my 2019 Ford Edge and had major fitment issues. The bolt pattern is completely wrong despite compatibility listing.
Works perfectly on my 2019 Mazda CX-5. Don't listen to the Ford owners having issues.
I have a 2017 Lincoln MKC and this hub assembly fit perfectly. No alignment issues whatsoever.
Doesn't fit right on my 2019 Ford Edge. Had to return and get the Edge-specific version.
Worked great on my 2018 Lincoln MKC - easy swap and resolved my wheel bearing noise.
I'm a shop owner and we've installed these on multiple 2017-2018 Ford Escapes and Lincoln MKCs with no issues. However, we've had consistent problems fitting these on 2019 Ford Escape, Edge, and 2019 Lincoln models. Manufacturer needs to update their compatibility list.
The catalog says it fits 2019 Ford C-Max but I had to drill new holes to make it work. Very frustrating.
Perfect fit for my 2017 Mazda CX-5, even though some reviewers say it only works on Fords.
Bought this for my 2019 Lincoln MKC and the bolt holes don't align properly. Had to return it."""

# Text area for reviews
st.write("""The text area below contains sample reviews for a front wheel hub assembly. You can modify these or add your own reviews for any product, then click 'Analyze Reviews' to detect patterns of fitment or compatibility problems.""")
reviews = st.text_area("Customer Reviews for Front Wheel Hub Assembly", 
                       value=default_reviews,
                       height=100)

# Function to call OpenAI API for fitment issue detection
def detect_fitment_issues(reviews_text: str, api_key: str):
    """Send reviews to OpenAI's model to detect fitment issues"""
    
    # Create a system prompt for fitment issue detection
    system_prompt = """You are a fitment issue detection system for auto parts. Analyze customer reviews to identify patterns of fitment issues by vehicle year/make/model/submodel.
        
    JSON format: 
    {
        "detected_issues": [
            {
                "vehicle": "YEAR MAKE MODEL SUBMODEL",
                "issue_description": "Brief description of the fitment issue",
                "confidence": "HIGH/MEDIUM/LOW based on number of reports",
                "affected_reviews": [list of review numbers or quotes]
            }
        ],
        "summary": "Overall assessment of fitment issues found"
    }
    Specifically mentioning submodels is important. For example, "2018 Ford Escape SE" is different from "2018 Ford Escape Titanium".
    """
    
    # Status container to show information about the process
    status_container = st.container()
    
    with status_container:
        st.write("### Processing Steps")
        step1 = st.empty()
        step2 = st.empty()
        step3 = st.empty()
        
        # Step 1: Collecting reviews
        step1.success("✅ Collected customer reviews")
        
        # Step 2: Building request
        step2.info("🔧 Building API request...")
    
    # Create the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-4.1-nano",
        #"model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system", 
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"Analyze these reviews for fitment issues:\n\n{reviews_text}"
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
        st.error(f"Error calling OpenAI API: {str(e)}")
        return {"error": str(e)}, status_container

# Go button
go_button = st.button("Analyze Reviews", type="primary")

# Process when user clicks the Go button
if go_button and api_key and reviews:
    # Call OpenAI API
    response, status_container = detect_fitment_issues(reviews, api_key)
    
    # Display formatted results
    if "error" in response:
        st.error(f"Error: {response['error']}")
    elif "choices" in response and len(response["choices"]) > 0:
        try:
            # Extract and parse the JSON response
            content = response["choices"][0]["message"]["content"]
            analysis_data = json.loads(content)
            
            # Display analysis results
            st.subheader("AI Analysis Result")
            
            # Display detected issues
            if "detected_issues" in analysis_data and analysis_data["detected_issues"]:
                for i, issue in enumerate(analysis_data["detected_issues"]):
                    st.markdown(f"**Vehicle:** {issue['vehicle']}")
                    st.markdown(f"**Issue:** {issue['issue_description']}")
                    st.markdown(f"**Confidence:** {issue['confidence']}")
                    
                    # Format the affected reviews
                    if "affected_reviews" in issue:
                        affected = ", ".join([str(rev) for rev in issue['affected_reviews']])
                        st.markdown(f"**Found in reviews:** {affected}")
                    
                    st.markdown("---")
                
                # Display summary
                if "summary" in analysis_data:
                    st.markdown(f"**Summary:** {analysis_data['summary']}")
            else:
                st.success("No significant fitment issues detected in these reviews.")
                
        except json.JSONDecodeError:
            st.error("Failed to parse response as JSON")
            st.text(content)
    else:
        st.error("No response received from API")
elif go_button and not api_key:
    st.warning("Please enter your API key to analyze reviews.")