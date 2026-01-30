import time
import requests
from duckduckgo_search import DDGS
from googlesearch import search as google_search

def search_topic(topic, num_results=5):
    """
    Attempts to search using DuckDuckGo, falls back to Google Search,
    and finally returns a simple placeholder if all else fails.
    """
    print(f"  ...trying DuckDuckGo for '{topic}'...")
    try:
        results = list(DDGS().text(topic, max_results=num_results))
        if results:
            return results
    except Exception as e:
        print(f"  DuckDuckGo failed: {e}")

    print(f"  ...trying Google Search for '{topic}'...")
    try:
        # Google search returns objects, we need to convert them to dicts or similar structure
        g_results = []
        for res in google_search(topic, num_results=num_results, advanced=True):
            g_results.append({
                'title': res.title,
                'href': res.url,
                'body': res.description
            })
        if g_results:
            return g_results
    except Exception as e:
        print(f"  Google Search failed: {e}")

    print("  ...all search methods failed.")
    return []

def format_search_results(results):
    if not results:
        return "No specific research data found. Please fetch general knowledge about this topic."
    
    formatted = []
    for result in results:
        title = result.get('title', 'No Title')
        url = result.get('href', 'No URL')
        body = result.get('body', 'No Description')
        formatted.append(f"Title: {title}\nURL: {url}\nDescription: {body}")
    
    return "\n\n".join(formatted)
