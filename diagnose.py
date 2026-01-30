import os
from google import genai
from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv()

# Test Gemini Models List
print("--- Listing Available Gemini Models ---")
try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    # In google-genai, list_models might be different, let's try iterating
    # Use standard list method if available or try to catch the error
    try:
        for model in client.models.list():
            if "generateContent" in model.supported_generation_methods:
                print(f"Found model: {model.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
        
    print("\n--- Testing Specific Models ---")
    test_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]
    for m in test_models:
        try:
            print(f"Testing {m}...")
            client.models.generate_content(model=m, contents="Hi")
            print(f"SUCCESS: {m}")
            break # Stop after first success
        except Exception as e:
            print(f"FAIL {m}: {e}")

except Exception as e:
    print(f"Client init error: {e}")

# Test Search Backends
print("\n--- Testing Search Backends ---")
backends = ["api", "html", "lite"]
for backend in backends:
    try:
        print(f"Testing backend: {backend}")
        results = list(DDGS().text("AI trends 2026", max_results=3, backend=backend))
        print(f"Results for {backend}: {len(results)}")
        if results:
            print(results[0])
            break # Use the first working backend
    except Exception as e:
        print(f"Backend {backend} error: {e}")
