import os
import time
from google import genai
from googlesearch import search
from dotenv import load_dotenv

load_dotenv()

# 1. Properly List Models
print("--- Listing Available Models (Attempt 2) ---")
try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    # The models.list() returns an iterator of Model objects
    # Let's inspect the first one to know attributes
    for model in client.models.list():
        # Just print names of first 20 valid models
        print(f"Model: {model.name}")
except Exception as e:
    print(f"Error listing models: {e}")

# 2. Test Google Search with minimal load
print("\n--- Testing Google Search (Fallback) ---")
try:
    print("Searching for 'Python' (1 result)...")
    # Add delay to respect rate limits if we were blocked
    time.sleep(2) 
    results = list(search("Python", num_results=1, advanced=True))
    print(f"Found {len(results)} results")
    if results:
        print(f"First result: {results[0].title} - {results[0].url}")
except Exception as e:
    print(f"Google Search Error: {e}")
