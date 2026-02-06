import requests
from config import PEXELS_API_KEY, PIXABAY_API_KEY, PEXELS_VIDEO_URL, PEXELS_IMAGE_URL, PIXABAY_URL, PIXABAY_IMAGE_URL, NEGATIVE_KEYWORDS, CORPORATE_NEGATIVE

def is_talking_head(video_data):
    tags = video_data.get('tags', '') if isinstance(video_data.get('tags'), str) else ''
    description = video_data.get('url', '').lower()
    
    for keyword in NEGATIVE_KEYWORDS:
        if keyword.lower() in tags.lower() or keyword.lower() in description:
            return True
    return False

def is_corporate_generic(video_data):
    tags = video_data.get('tags', '') if isinstance(video_data.get('tags'), str) else ''
    
    for keyword in CORPORATE_NEGATIVE:
        if keyword.lower() in tags.lower():
            return True
    return False

def search_pexels_video(query, per_page=5):
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": per_page, "orientation": "landscape"}
    
    response = requests.get(PEXELS_VIDEO_URL, headers=headers, params=params)
    
    if response.status_code == 429:
        return {"error": "rate_limit", "videos": []}
    
    if response.status_code != 200:
        return {"error": f"status_{response.status_code}", "videos": []}
    
    data = response.json()
    videos = data.get('videos', [])
    
    filtered = [v for v in videos if not is_talking_head(v) and not is_corporate_generic(v)]
    
    return {"error": None, "videos": filtered}

def search_pixabay_video(query, per_page=5):
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "per_page": per_page,
        "video_type": "film",
        "orientation": "horizontal"
    }
    
    response = requests.get(PIXABAY_URL, params=params)
    
    if response.status_code == 429:
        return {"error": "rate_limit", "videos": []}
    
    if response.status_code != 200:
        return {"error": f"status_{response.status_code}", "videos": []}
    
    data = response.json()
    videos = data.get('hits', [])
    
    filtered = [v for v in videos if not is_talking_head(v) and not is_corporate_generic(v)]
    
    return {"error": None, "videos": filtered}

def search_pexels_image(query, per_page=3):
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": per_page, "orientation": "landscape"}
    
    response = requests.get(PEXELS_IMAGE_URL, headers=headers, params=params)
    
    if response.status_code == 429:
        return {"error": "rate_limit", "photos": []}
    
    if response.status_code != 200:
        return {"error": f"status_{response.status_code}", "photos": []}
    
    data = response.json()
    return {"error": None, "photos": data.get('photos', [])}

def search_pixabay_image(query, per_page=3):
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "per_page": per_page,
        "image_type": "photo",
        "orientation": "horizontal"
    }
    
    response = requests.get(PIXABAY_IMAGE_URL, params=params)
    
    if response.status_code == 429:
        return {"error": "rate_limit", "hits": []}
    
    if response.status_code != 200:
        return {"error": f"status_{response.status_code}", "hits": []}
    
    data = response.json()
    return {"error": None, "hits": data.get('hits', [])}

def get_pexels_video_url(video):
    files = video.get('video_files', [])
    for f in files:
        if f.get('quality') == 'hd' and f.get('width', 0) >= 1280:
            return f.get('link')
    return files[0].get('link') if files else None

def get_pixabay_video_url(video):
    videos = video.get('videos', {})
    if 'large' in videos:
        return videos['large'].get('url')
    if 'medium' in videos:
        return videos['medium'].get('url')
    if 'small' in videos:
        return videos['small'].get('url')
    return None

def get_pexels_image_url(photo):
    return photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')

def get_pixabay_image_url(hit):
    return hit.get('largeImageURL') or hit.get('webformatURL')

def search_media(query, media_type="video"):
    if media_type == "video":
        pexels_result = search_pexels_video(query)
        if pexels_result['videos']:
            video = pexels_result['videos'][0]
            return {
                "source": "pexels",
                "type": "video",
                "url": get_pexels_video_url(video),
                "error": None
            }
        
        pixabay_result = search_pixabay_video(query)
        if pixabay_result['videos']:
            video = pixabay_result['videos'][0]
            return {
                "source": "pixabay",
                "type": "video",
                "url": get_pixabay_video_url(video),
                "error": None
            }
        
        return {
            "source": None,
            "type": None,
            "url": None,
            "error": pexels_result.get('error') or pixabay_result.get('error') or "no_results"
        }
    
    else:
        pexels_result = search_pexels_image(query)
        if pexels_result.get('photos'):
            photo = pexels_result['photos'][0]
            return {
                "source": "pexels",
                "type": "image",
                "url": get_pexels_image_url(photo),
                "error": None
            }
        
        pixabay_result = search_pixabay_image(query)
        if pixabay_result.get('hits'):
            hit = pixabay_result['hits'][0]
            return {
                "source": "pixabay",
                "type": "image",
                "url": get_pixabay_image_url(hit),
                "error": None
            }
        
        return {
            "source": None,
            "type": None,
            "url": None,
            "error": pexels_result.get('error') or pixabay_result.get('error') or "no_results"
        }
