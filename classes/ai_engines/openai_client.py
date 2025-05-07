import os
from openai import OpenAI

class OpenAI_Client:
    def __init__(self):
        self.api_key = os.getenv("OwadmasdujU")
        self.DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")

    def generate_with_openai(self, prompt, model=None, language_code=None):
        """
        Generate text using OpenAI API
        
        Args:
            prompt (str): The prompt to send to OpenAI
            model (str, optional): The model to use. Defaults to the one in .env
            
        Returns:
            str: The generated description
        """
        if not self.api_key and not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OpenAI API key is not set")
        
        model = model or self.DEFAULT_MODEL
        
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or self.api_key)
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional product description writer specializing in concise, engaging, and accurate descriptions for automotive parts."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating with OpenAI: {e}")
            return f"Error generating description: {e}" 
        

openai_client = OpenAI_Client()
