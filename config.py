import os
from dotenv import load_dotenv

# Load environment variables from .env if available
load_dotenv()

# Gemini API key – ensure this is valid
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "PASTE_YOUR_KEY_HERE_FROM_DESKTOP_key.txt"

if not GEMINI_API_KEY or GEMINI_API_KEY.startswith("PASTE_YOUR_KEY"):
    raise ValueError("❌ GEMINI_API_KEY not set! Please update config.py or .env with your actual key.")
