
class PIES_Prompt_Builder:
    def __init__(self):
        self.invalid_characters = ['<', '>', '&', '"', "'", '`', '#', '*', '_', '^', '~', '|', ':', ';', '/', '\\', '@', '$', '%', '+', '=', '{', '}', '[', ']', '(', ')']
        pass

    def convert_language_code_to_name(self, language_code):
        """Convert language code to language name"""
        return {
            "ENGL": "English",
            "SPAN": "Spanish",
            "FREN": "French",
            "GERM": "German"
        }.get(language_code, "English")
    

    def get_pies_description_codes(self):
        """Return PIES description codes with explanations"""
        return {
            "SHORT_DESC": "A brief label used when only a few characters can be displayed, providing a quick identification of the product. Use this once per part number.",
            "FIT_SUMMARY": "A basic summary showing general fitment details like compatible years, makes, and models (e.g., 2010-2015 Chevy Silverado). Do not include detailed fitment data here; that should be shared through ACES. For more than one fitment, repeat this code.",
            "USER_WARNING": "Safety alerts or caution messages meant for the product user. These can be bullet points or simple statements. Each warning should be shared individually, with the option to assign a display order if needed. Also aligns with 'Caution' qualifier types in ACES® Qdb.",
            "FULL_DESC": "A complete description outlining what the product is. Only one description should be provided per part number using this code.",
            "EXTENDED_DESC": "A detailed, extended product description giving a broader overview of the item. Use this code only once per part number.",
            "FEATURE_BENEFIT": "Feature and benefit highlights explaining why the product stands out. Includes functional details or value-added characteristics. Each point should be sent separately and can be ordered using a sequence value. Supports the main marketing description.",
            "IMPORTANT_INFO": "Important notes for both consumers and technicians about the product. These may be shared as single statements or grouped lists. Each entry should be provided individually. These align with 'Informational' qualifier types in ACES® Qdb.",
            "INSTALL_GUIDE": "Helpful guidance or tips for installing the product. Do not use this for full installation instructions. Each suggestion should be sent separately, with optional display sequence. Tied to 'Installation' qualifier types in ACES® Qdb.",
            "INVOICE_DESC": "A description used specifically for invoices to describe the product being sold. This code should only appear once per part number.",
            "SEARCH_TERMS": "Keywords that help improve online search visibility for the product, including slang or common alternative terms. Provide one keyword per entry, repeating the code if needed for multiple words.",
            "LABEL_TEXT": "A short label description meant for packaging or shelf/bin identification. Use only once per part number.",
            "MARKETING_COPY": "A marketing paragraph designed to promote the product on web pages. It highlights key features, benefits, and unique selling points, supported by additional FEATURE_BENEFIT statements. Use this once per part number.",
            "CONDENSED_DESC": "A shortened product description intended for use where space is limited. Use only one entry per part number.",
            "ALT_NAMES": "Alternate names or search-friendly terms for the product. Share one term at a time by repeating this code as needed.",
            "TITLE_DESC": "An SEO-focused description combining the product name with key attributes for better online search results. Provide one entry per part number using this code.",
            "TECH_TIP_INTRO": "An introductory paragraph for the technical tips section of a product page. Sets the stage for supporting TECH_TIP_DETAIL statements. Use only once per part number.",
            "TECH_TIP_DETAIL": "Individual technical tips offering advice or best practices for working with the product. Share each tip separately, with optional sequencing. Supports the main TECH_TIP_INTRO description."
        }

    # Function to get PIES description max lengths
    def get_pies_description_max_lengths(self):
        """Return PIES description max lengths"""
        return {
            "SHORT_DESC": 12,
            "FIT_SUMMARY": 240,
            "USER_WARNING": 500,
            "FULL_DESC": 80,
            "EXTENDED_DESC": 240,
            "FEATURE_BENEFIT": 240,
            "IMPORTANT_INFO": 500,
            "INSTALL_GUIDE": 500,
            "INVOICE_DESC": 40,
            "SEARCH_TERMS": 80,
            "LABEL_TEXT": 80,
            "MARKETING_COPY": 2000,
            "CONDENSED_DESC": 20,
            "ALT_NAMES": 80,
            "TITLE_DESC": 200,
            "TECH_TIP_INTRO": 2000,
            "TECH_TIP_DETAIL": 240
        }

    # Function to validate PIES description
    def validate_pies_description(self, description_type, text):
        """Validate description according to PIES standards"""
        validation_results = {
            "is_valid": True,
            "issues": []
        }
        
        # Check description length limits
        max_lengths = self.get_pies_description_max_lengths()
        
        if len(text) > max_lengths.get(description_type, 255):
            validation_results["is_valid"] = False
            validation_results["issues"].append(f"Description exceeds maximum length of {max_lengths.get(description_type, 255)} characters")
        
        # Check for invalid characters
        invalid_chars = ['<', '>', '&', '"', "'"]
        for char in invalid_chars:
            if char in text:
                validation_results["is_valid"] = False
                validation_results["issues"].append(f"Description contains invalid character: {char}")
        
        return validation_results

    # Function to build PIES prompt
    def build_pies_prompt(self, product_info, description_type, language_code):
        """
        Build a prompt for the AI to generate a PIES-compliant product description
            
        Args:
            product_info (dict): Information about the automotive part
                Expected keys:
                - part_number: The part number
                - product_category: Type of product (e.g., Ignition Coil, Oxygen Sensor)
                - brand: Brand name
                - part_type: Specific part type
                - engine_application: Engine compatibility (optional)
                - material: Material of the part (optional)
                - fitment: Fitment information (optional)
            description_type (str): PIES description code
        
        Returns:
            str: A formatted prompt for the AI
        """
        part_number = product_info.get('part_number', '')
        product_category = product_info.get('product_category', '')
        brand = product_info.get('brand', '')
        part_type = product_info.get('part_type', '')
        engine_application = product_info.get('engine_application', '')
        material = product_info.get('material', '')
        fitment = product_info.get('fitment', '')
        
        # Convert language code to language name
        language_name = self.convert_language_code_to_name(language_code)
        
        # Map description types to their context
        description_contexts = self.get_pies_description_codes()
        
        # Get context for the description type
        context = description_contexts.get(description_type, "product description")
        
        # Set max length based on description type
        max_lengths = self.get_pies_description_max_lengths()
        max_length = max_lengths.get(description_type, 255)
        adjusted_max_length = max_length - (max_length * 0.2)
        
        # Build the base prompt
        prompt = f"""You are a professional automotive aftermarket content writer specializing in PIES-compliant product descriptions. It is extremely IMPORTANT that you should make sure that the description is not longer than {max_length} characters.

Write a {context} for part number {part_number}, which is a {product_category} from {brand}. This must be written in {language_name}.
        """
        
        # Add part type if available
        if part_type:
            prompt += f"Specific part type: {part_type}.\n"
        
        # Add engine application if available
        if engine_application:
            prompt += f"Engine application: {engine_application}.\n"
        
        # Add material if available
        if material:
            prompt += f"Material: {material}.\n"
        
        # Add fitment information if available
        if fitment:
            prompt += f"Fitment information: {fitment}.\n"
        
        # Add specific instructions based on description type
        # TODO: Clean up to be more dynamic and not hardcoded
        if description_type == "SHORT_DESC":
            prompt += f"""
For this SHORT DESCRIPTION:
1. Create a brief label for quick product identification
2. Be extremely concise (under {adjusted_max_length} characters)
3. Focus only on the most essential information
4. Use abbreviated terms common in the automotive industry when necessary
5. Do not include any fitment information
        """
        elif description_type == "FIT_SUMMARY":
            prompt += f"""
For this FITMENT SUMMARY:
1. Provide a basic summary of compatible years, makes, and models
2. Keep it concise and focused on primary applications
3. Example: "2018-2022 Mitsubishi Outlander Sport (Liter: 2.0, 2.4 & Cylinder: 4 & Block: L); 2017-2019 Mitsubishi RVR (Liter: 2.0, 2.4 & Cylinder: 4 & Block: L); 2018 Mitsubishi Outlander PHEV (Liter: 2.0 & Cylinder: 4 & Block: L); 2014-2019 Mitsubishi Outlander (Liter: 2.4 & Cylinder: 4 & Block: L)"
4. Do not include any other product detailed
5. Be extremely concise (under {adjusted_max_length} characters)
        """
        elif description_type == "USER_WARNING":
            prompt += f"""
For this USER WARNING:
1. Create clear safety alerts or caution messages
2. Use direct, unambiguous language about potential hazards
3. Format as bullet points or simple statements
4. Focus on critical safety information the user must know
5. Be extremely concise (under {adjusted_max_length} characters)
6. Do not include any fitment information
        """
        elif description_type == "FULL_DESC":
            prompt += f"""
For this FULL DESCRIPTION:
1. Provide a complete description of what the product is
2. Include comprehensive details about features, materials, and purpose
3. Use professional, technical language appropriate for the industry
4. Create a thorough but concise explanation of the part
5. Be extremely concise (under {adjusted_max_length} characters)
6. Do not include any fitment information
            """
        elif description_type == "EXTENDED_DESC":
            prompt += f"""
For this EXTENDED DESCRIPTION:
1. Create a detailed, extended overview of the product
2. Include comprehensive information about features, benefits, and applications
3. Use professional terminology with thorough explanations
4. Provide more depth than the standard description
5. Be extremely concise (under {adjusted_max_length} characters)
6. Do not include any fitment information
            """
        elif description_type == "FEATURE_BENEFIT":
            prompt += f"""
For this FEATURE/BENEFIT:
1. Highlight a specific feature and its direct benefit to the customer
2. Use clear cause-and-effect language (e.g., "Precision-engineered for longer service life")
3. Focus on what differentiates this part from competitors
4. Emphasize value to the customer
5. Be extremely concise (under {adjusted_max_length} characters)
6. Do not include any fitment information
            """
        elif description_type == "IMPORTANT_INFO":
            prompt += f"""
For this IMPORTANT INFORMATION:
1. Provide critical notes for consumers and technicians
2. Focus on non-safety information that's still essential to know
3. Use clear, direct language
4. Include information that affects usage, performance, or installation
5. Be extremely concise (under {adjusted_max_length} characters)
6. Do not include any fitment information
            """
        elif description_type == "INSTALL_GUIDE":
            prompt += f"""
For this INSTALLATION GUIDE:
1. Provide helpful guidance or tips for installing the product
2. Include practical advice to avoid common installation problems
3. Mention any special tools or precautions needed
4. Keep instructions concise and focused on key points
5. Be extremely concise (under {adjusted_max_length} characters)
6. Do not include any fitment information
            """
        elif description_type == "INVOICE_DESC":
            prompt += f"""
For this INVOICE DESCRIPTION:
1. Create a clear, concise description for invoices
2. Include essential identifying information about the part
3. Use standard industry terminology
4. Focus on what's needed for accurate billing and inventory
5. Be extremely concise (under {adjusted_max_length} characters)
6. Do not include any fitment information
            """
        elif description_type == "SEARCH_TERMS":
            prompt += f"""
For this SEARCH TERMS:
1. Provide keywords that improve online search visibility
2. Include industry slang or common alternative terms
3. Focus on terms customers might use when searching
4. Keep each term relevant and specific to the product
5. Be extremely concise (under {adjusted_max_length} characters)
6. Do not include any fitment information
            """
        elif description_type == "LABEL_TEXT":
            prompt += f"""
For this LABEL TEXT:
1. Create a short description for packaging or shelf/bin identification
2. Be extremely concise while maintaining clarity
3. Include only the most essential identifying information
4. Use standard industry terminology
5. Be extremely concise (under {adjusted_max_length} characters)
6. Do not include any fitment information
            """
        elif description_type == "MARKETING_COPY":
            prompt += f"""
For this MARKETING COPY:
1. Create compelling, persuasive content for web pages
2. Highlight key features, benefits, and unique selling points
3. Use engaging language that appeals to customers
4. Focus on what makes this part a good purchase decision
5. Be extremely concise (under {adjusted_max_length} characters)
6. Do not include any fitment information
            """
        elif description_type == "CONDENSED_DESC":
            prompt += f"""
For this CONDENSED DESCRIPTION:
1. Create a shortened product description for space-limited contexts
2. Include only the most important features and specifications
3. Use concise, efficient language
4. Maintain clarity while being extremely brief
5. Be extremely concise (under {adjusted_max_length} characters)
6. Do not include any fitment information
            """
        elif description_type == "ALT_NAMES":
            prompt += f"""
For this ALTERNATE NAMES:
1. Provide alternate names or search-friendly terms for the product
2. Include common industry variations in terminology
3. Focus on terms customers might use when searching
4. Keep each term accurate and relevant
5. Be extremely concise (under {adjusted_max_length} characters)
6. Do not include any fitment information
            """
        elif description_type == "TITLE_DESC":
            prompt += f"""
For this TITLE DESCRIPTION:
1. Create an SEO-focused description combining product name with key attributes
2. Format for optimal online search results
3. Include the most important specifications or features
4. Keep it concise but comprehensive for search purposes
5. Be extremely concise (under {adjusted_max_length} characters)
6. Do not include any fitment information
            """
        elif description_type == "TECH_TIP_INTRO":
            prompt += f"""
For this TECHNICAL TIP INTRODUCTION:
1. Create an introductory paragraph for technical tips
2. Set the context for why these tips are important
3. Use professional, knowledgeable language
4. Prepare the reader for the detailed tips that will follow
5. Be extremely concise (under {adjusted_max_length} characters)
6. Do not include any fitment information
            """
        elif description_type == "TECH_TIP_DETAIL":
            prompt += f"""
For this TECHNICAL TIP DETAIL:
1. Provide a specific technical tip for working with the product
2. Offer practical advice or best practices
3. Use clear, instructional language
4. Focus on helping technicians or DIY customers succeed with the part
5. Be extremely concise (under {adjusted_max_length} characters)
6. Do not include any fitment information
            """
        
        # Add PIES compliance instructions
        prompt += f"""
PIES XML COMPLIANCE REQUIREMENTS:
1. Do not include HTML or XML tags in your description
2. IMPORTANT: Must NOT include special characters like {', '.join(self.invalid_characters)}. Do not include line breaks in your description.
3. Do not include marketing slogans or excessive capitalization
4. Focus on factual, specific information about the part
5. Respond with ONLY the description text, nothing else
        """
        # Add character limit instruction
        prompt += f"\nIMPORTANT: Maximum length is {adjusted_max_length} characters. Do not exceed this limit."

        return prompt 

pies_prompt_builder = PIES_Prompt_Builder()