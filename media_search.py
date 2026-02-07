import requests
from config import SERPER_API_KEY
import time
import random

SERPER_IMAGES_URL = "https://google.serper.dev/images"

def search_google_images(query, num_results=5):
    if not SERPER_API_KEY:
        return {"error": "missing_api_key", "url": None, "type": None}
    
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "q": query,
        "num": num_results
    }
    
    response = requests.post(SERPER_IMAGES_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        images = data.get("images", [])
        
        if images:
            best_image = images[0]
            return {
                "url": best_image.get("imageUrl"),
                "title": best_image.get("title"),
                "source": best_image.get("source"),
                "type": "image",
                "source_api": "google",
                "all_results": images[:num_results]
            }
        return {"error": "no_results", "url": None, "type": None}
    
    elif response.status_code == 429:
        return {"error": "rate_limit", "url": None, "type": None}
    
    else:
        return {"error": f"api_error_{response.status_code}", "url": None, "type": None}

def search_media(query, media_type="image"):
    result = search_google_images(query)
    
    if result.get("url"):
        return result
    
    return {"error": result.get("error", "not_found"), "url": None, "type": None}
