import os
import requests
import json
from PIL import Image, ImageDraw, ImageFont

def ensure_directory(path):
    os.makedirs(path, exist_ok=True)
    return path

def download_file(url, filepath, headers=None):
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    return False

def create_black_placeholder(filepath, width=1920, height=1080):
    img = Image.new('RGB', (width, height), color='black')
    img.save(filepath)
    return filepath

def create_text_overlay_png(text, filepath, width=1920, height=1080):
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font_size = 120
    font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x + 3, y + 3), text, font=font, fill=(0, 0, 0, 200))
    draw.text((x, y), text, font=font, fill=(255, 215, 0, 255))
    
    img.save(filepath, 'PNG')
    return filepath

def extract_numbers(text):
    import re
    numbers = re.findall(r'[\$€£]?\d+(?:,\d{3})*(?:\.\d+)?(?:%|M|B|K)?', text)
    return numbers

def contains_number_or_currency(text):
    import re
    return bool(re.search(r'[\$€£]?\d+(?:,\d{3})*(?:\.\d+)?(?:%|M|B|K)?', text))

def sanitize_filename(name):
    import re
    return re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')[:50]

def write_json(data, filepath):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def append_to_file(filepath, content):
    with open(filepath, 'a') as f:
        f.write(content + '\n')

def get_video_duration(filepath):
    import subprocess
    result = subprocess.run(
        ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', filepath],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return float(result.stdout.strip())
    return 0

def trim_video(input_path, output_path, max_duration=3):
    import subprocess
    subprocess.run(
        ['ffmpeg', '-y', '-i', input_path, '-t', str(max_duration), '-c', 'copy', output_path],
        capture_output=True
    )
    os.remove(input_path)
    return output_path
