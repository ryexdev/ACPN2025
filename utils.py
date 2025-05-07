import os
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file"""
    # First try to load from the app directory
    if os.path.exists("/app/.env"):
        load_dotenv("/app/.env")
    # Then try the current directory
    elif os.path.exists(".env"):
        load_dotenv()
    else:
        print("Warning: .env file not found") 