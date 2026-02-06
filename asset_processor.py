import os
import requests
from config import MAX_VIDEO_DURATION, KEN_BURNS_INSTRUCTION
from utils import download_file, create_black_placeholder, create_text_overlay_png, trim_video, contains_number_or_currency, extract_numbers, ensure_directory

def download_and_process_video(url, output_path, headers=None):
    temp_path = output_path + ".temp.mp4"
    
    success = download_file(url, temp_path, headers)
    if not success:
        return None
    
    trimmed_path = trim_video(temp_path, output_path, MAX_VIDEO_DURATION)
    return trimmed_path

def download_and_process_image(url, output_path, headers=None):
    success = download_file(url, output_path, headers)
    if not success:
        return None
    return output_path

def create_asset(beat_data, media_result, assets_dir, index, phase):
    prefix = f"{str(index).zfill(3)}_{phase}"
    
    if media_result.get('url') and media_result.get('type') == 'video':
        output_path = os.path.join(assets_dir, f"{prefix}_Asset.mp4")
        result = download_and_process_video(media_result['url'], output_path)
        if result:
            return {
                "filename": f"{prefix}_Asset.mp4",
                "type": "video",
                "source": media_result.get('source'),
                "instruction": None,
                "success": True
            }
    
    elif media_result.get('url') and media_result.get('type') == 'image':
        output_path = os.path.join(assets_dir, f"{prefix}_Asset.jpg")
        result = download_and_process_image(media_result['url'], output_path)
        if result:
            return {
                "filename": f"{prefix}_Asset.jpg",
                "type": "image",
                "source": media_result.get('source'),
                "instruction": KEN_BURNS_INSTRUCTION,
                "success": True
            }
    
    placeholder_path = os.path.join(assets_dir, f"{prefix}_Placeholder.jpg")
    create_black_placeholder(placeholder_path)
    return {
        "filename": f"{prefix}_Placeholder.jpg",
        "type": "placeholder",
        "source": None,
        "instruction": KEN_BURNS_INSTRUCTION,
        "success": False,
        "error": media_result.get('error', 'unknown_error')
    }

def create_number_overlay(beat_text, assets_dir, index, phase):
    if not contains_number_or_currency(beat_text):
        return None
    
    numbers = extract_numbers(beat_text)
    if not numbers:
        return None
    
    prefix = f"{str(index).zfill(3)}_{phase}"
    overlay_path = os.path.join(assets_dir, f"{prefix}_Overlay.png")
    create_text_overlay_png(numbers[0], overlay_path)
    
    return {
        "filename": f"{prefix}_Overlay.png",
        "text": numbers[0],
        "instruction": "Overlay in bold yellow Montserrat font, center screen"
    }
