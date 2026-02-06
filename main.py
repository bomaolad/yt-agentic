import os
import sys
from config import GEMINI_API_KEY, PEXELS_API_KEY, PIXABAY_API_KEY
from llm_processor import process_script, generate_ai_prompt
from media_search import search_media
from asset_processor import create_asset, create_number_overlay
from output_generator import create_project_structure, add_image_prompt, finalize_outputs

def validate_api_keys():
    missing = []
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    if not PEXELS_API_KEY:
        missing.append("PEXELS_API_KEY")
    if not PIXABAY_API_KEY:
        missing.append("PIXABAY_API_KEY")
    
    if missing:
        print(f"❌ Missing API keys in .env file: {', '.join(missing)}")
        print("\nPlease add the following to your .env file:")
        for key in missing:
            print(f"  {key}=your_key_here")
        print("\nGet free API keys at:")
        print("  - Gemini: https://aistudio.google.com/apikey")
        print("  - Pexels: https://www.pexels.com/api/")
        print("  - Pixabay: https://pixabay.com/api/docs/")
        return False
    return True

def get_script_input():
    print("\n" + "=" * 60)
    print("🎬 YOUTUBE VISUAL ASSETS GENERATOR")
    print("=" * 60)
    print("\nPaste your YouTube script below.")
    print("When done, press Enter twice (empty line) to process.\n")
    
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    
    return " ".join([l for l in lines if l.strip()])

def get_project_title():
    print("\n📁 Enter a project title (for folder name):")
    title = input("> ").strip()
    return title if title else "Video_Project"

def process_beat(beat_data, paths):
    print(f"\n  [{beat_data['index']:03d}] Processing: \"{beat_data['beat'][:40]}...\"")
    
    analysis = beat_data['analysis']
    ai_prompt = None
    asset_result = None
    
    if analysis.get('type') == 'historical' and not analysis.get('is_abstract'):
        search_query = analysis.get('search_query', beat_data['beat'])
        print(f"       🔍 Searching for: {search_query}")
        
        media_result = search_media(search_query, "video")
        
        if media_result.get('error') == 'rate_limit':
            print("       ⚠️  Rate limited, trying image search...")
            media_result = search_media(search_query, "image")
        
        if media_result.get('url'):
            print(f"       ✅ Found {media_result['type']} from {media_result['source']}")
            asset_result = create_asset(
                beat_data,
                media_result,
                paths['assets_dir'],
                beat_data['index'],
                beat_data['phase']
            )
        else:
            print("       ⚠️  No footage found, generating AI prompt...")
            ai_prompt = generate_ai_prompt(beat_data['beat'])
    else:
        meme = analysis.get('meme_suggestion')
        if meme:
            print(f"       🎭 Meme suggestion: {meme}")
            media_result = search_media(meme, "image")
            if media_result.get('url'):
                print(f"       ✅ Found meme image from {media_result['source']}")
                asset_result = create_asset(
                    beat_data,
                    media_result,
                    paths['assets_dir'],
                    beat_data['index'],
                    beat_data['phase']
                )
        
        if not asset_result:
            print("       🎨 Generating cinematic AI prompt...")
            ai_prompt = generate_ai_prompt(beat_data['beat'])
    
    if ai_prompt:
        add_image_prompt(
            paths['image_prompts_path'],
            beat_data['index'],
            beat_data['phase'],
            ai_prompt
        )
        print(f"       📝 AI prompt saved")
        
        if not asset_result:
            asset_result = create_asset(
                beat_data,
                {"url": None, "type": None, "error": "ai_prompt_generated"},
                paths['assets_dir'],
                beat_data['index'],
                beat_data['phase']
            )
    
    overlay = create_number_overlay(
        beat_data['beat'],
        paths['assets_dir'],
        beat_data['index'],
        beat_data['phase']
    )
    
    if overlay:
        print(f"       🔢 Number overlay created: {overlay['text']}")
    
    return {
        "asset": asset_result,
        "ai_prompt": ai_prompt,
        "overlay": overlay
    }

def main():
    if not validate_api_keys():
        sys.exit(1)
    
    script_text = get_script_input()
    if not script_text.strip():
        print("❌ No script provided. Exiting.")
        sys.exit(1)
    
    project_title = get_project_title()
    
    print("\n" + "=" * 60)
    print("📊 ANALYZING SCRIPT")
    print("=" * 60)
    
    print("\n🧠 Breaking script into visual beats...")
    processed_beats = process_script(script_text)
    print(f"   Found {len(processed_beats)} visual beats")
    
    paths = create_project_structure(project_title)
    print(f"\n📁 Created project folder: {paths['project_dir']}")
    
    print("\n" + "=" * 60)
    print("🎥 GATHERING ASSETS")
    print("=" * 60)
    
    asset_results = []
    for beat_data in processed_beats:
        result = process_beat(beat_data, paths)
        asset_results.append(result)
    
    print("\n" + "=" * 60)
    print("📋 GENERATING OUTPUTS")
    print("=" * 60)
    
    summary = finalize_outputs(paths, processed_beats, asset_results, project_title)
    
    print(f"\n✅ COMPLETE!")
    print(f"   📁 Project folder: {summary['project_dir']}")
    print(f"   🎬 Total assets: {summary['assets_count']}")
    print(f"   ✅ Downloaded: {summary['successful']}")
    print(f"   📝 AI prompts: {summary['prompts_generated']}")
    print(f"\n📄 Output files:")
    print(f"   - Assets/          (video/image files)")
    print(f"   - Image_Prompts.txt (AI prompts for manual generation)")
    print(f"   - Editing_Notes.json (beat-to-asset mapping with SFX)")
    print(f"   - manifest.txt     (success/error log)")

if __name__ == "__main__":
    main()
