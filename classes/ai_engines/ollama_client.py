import os
import requests
import json
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ollama_client")

class Ollama_Client:
    def __init__(self):
        self.OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")

    def generate_with_ollama(self, prompt, model=None):
        """
        Generate text using Ollama API
        
        Args:
            prompt (str): The prompt to send to Ollama
            model (str, optional): The model to use. Defaults to the one in .env
            
        Returns:
            str: The generated description
        """
        model = model or self.DEFAULT_MODEL
        api_url = f"{self.OLLAMA_URL}/api/generate"
        
        # Create the system prompt
        system_prompt = "You are a professional product description writer specializing in concise, engaging, and accurate descriptions for automotive parts."
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            "model": model,
            "prompt": full_prompt,
            "temperature": 0.7,
            "max_tokens": 500,
            "stream": False  # Explicitly set to False to avoid streaming
        }
        
        logger.info(f"Sending request to Ollama at: {api_url}")
        logger.info(f"Using model: {model}")
        
        try:
            # Increase timeout to 60 seconds for model loading
            response = requests.post(api_url, json=payload, timeout=60)
            
            logger.info(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    # Try to parse as a complete JSON object
                    response_json = json.loads(response.text)
                    result = response_json.get("response", "").strip()
                    logger.info("Successfully generated text with Ollama")
                    return result
                except json.JSONDecodeError:
                    logger.info("Response appears to be streaming JSON. Trying to parse line by line.")
                    try:
                        # Handle streaming response format
                        full_response = ""
                        for line in response.text.strip().split('\n'):
                            if line:
                                try:
                                    json_obj = json.loads(line)
                                    if json_obj.get("response"):
                                        full_response += json_obj["response"]
                                except json.JSONDecodeError:
                                    logger.warning(f"Couldn't parse line as JSON: {line[:50]}...")
                        
                        if full_response:
                            logger.info("Successfully assembled response from streaming JSON")
                            return full_response.strip()
                        else:
                            error_message = f"No valid response content found in streaming output: {response.text[:100]}..."
                            logger.error(error_message)
                            return f"Error generating description: {error_message}"
                    except Exception as e:
                        error_message = f"Error processing streaming response: {e}. Response text: {response.text[:100]}..."
                        logger.error(error_message)
                        return f"Error generating description: {error_message}"
            else:
                error_message = f"Error from Ollama API: {response.status_code} - {response.text}"
                logger.error(error_message)
                # Try to check if Ollama is reachable
                try:
                    health_check = requests.get(f"{self.OLLAMA_URL}/api/tags", timeout=5)
                    logger.info(f"Ollama server is reachable: Status {health_check.status_code}")
                    if health_check.status_code == 200:
                        try:
                            models = health_check.json().get("models", [])
                            logger.info(f"Available models: {[m.get('name') for m in models]}")
                            if not models:
                                return f"Error: No models found in Ollama. Please pull the model '{model}' first."
                            elif not any(m.get('name') == model for m in models):
                                return f"Error: Model '{model}' not found. Available models: {[m.get('name') for m in models]}"
                        except json.JSONDecodeError:
                            logger.error("Could not parse JSON from health check")
                except Exception as health_e:
                    logger.error(f"Health check failed: {health_e}")
                    
                return f"Error generating description: {error_message}"
        except requests.exceptions.Timeout:
            error = "Request to Ollama timed out after 60 seconds. The model might be loading or too large."
            logger.error(error)
            return f"Error: {error}"
        except requests.exceptions.ConnectionError as ce:
            error = f"Connection to Ollama failed. Please ensure Ollama is running at {self.OLLAMA_URL}.\nDetails: {ce}"
            logger.error(error)
            logger.error(traceback.format_exc())
            return f"Error: Could not connect to Ollama server. Please make sure Ollama is running at {self.OLLAMA_URL}."
        except Exception as e:
            error = f"Error generating with Ollama: {e}"
            logger.error(error)
            logger.error(traceback.format_exc())
            return f"Error generating description: {e}" 
        
ollama_client = Ollama_Client()
