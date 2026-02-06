import requests
import json
import time
import random
from config import BEAT_LENGTH_MIN, BEAT_LENGTH_MAX, PHASES, AI_STYLE_KEYWORDS, SFX_MAPPINGS
import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL_NAME = "deepseek-chat"

def generate_content(prompt, retries=5, initial_delay=2.0):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for video editing tasks. Always respond with valid JSON when asked."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    for attempt in range(retries):
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        elif response.status_code == 429:
            if attempt == retries - 1:
                raise Exception(f"Rate limit exceeded after {retries} retries")
            sleep_time = (initial_delay * (2 ** attempt)) + random.uniform(0.1, 1.0)
            print(f"       ⚠️  Rate limit hit (429). Waiting {sleep_time:.1f}s before retry {attempt + 1}/{retries}...")
            time.sleep(sleep_time)
        else:
            raise Exception(f"DeepSeek API error {response.status_code}: {response.text}")
    
    return ""

segment_script_to_beats = lambda script_text: generate_content(
    f"""You are a video editor AI. Break this script into "Visual Beats" for a YouTube video.

RULES:
1. Each beat should be 25-30 characters (roughly 1.5-2 seconds of spoken word)
2. Each beat should be a natural phrase or idea
3. Return ONLY a valid JSON array of beats, no other text

Script: "{script_text}"

Return format example:
["In 1994 Steve Jobs", "returned to Apple", "The company was failing", "But he had a plan"]"""
)

def analyze_beats_batch(beats):
    beats_json = json.dumps(beats)
    sfx_categories = list(SFX_MAPPINGS.keys())
    
    prompt = f"""Analyze these video script beats in batch.

Input Beats: {beats_json}

For EACH beat, determine:
1. Visual Type: "historical" (if specific person/brand/year mentioned) or "abstract"
2. Search Query: specific query for stock footage (if historical) or empty string
3. Meme Suggestion: popular meme name (if abstract and fits), else null
4. SFX Category: best fit from {sfx_categories}

Return ONLY a valid JSON array of objects, one for each input beat, in the same order.

Example Output format:
[
  {{
    "beat": "In 1994 Steve Jobs",
    "type": "historical",
    "search_query": "Steve Jobs 1994",
    "meme_suggestion": null,
    "sfx": "success"
  }},
  {{
    "beat": "The plan failed",
    "type": "abstract",
    "search_query": "",
    "meme_suggestion": "sad pablo escobar",
    "sfx": "failure"
  }}
]"""
    return generate_content(prompt)

generate_ai_prompt = lambda beat_text, context="": generate_content(
    f"""Generate a cinematic AI image prompt for this video beat.

Beat: "{beat_text}"
Context: {context if context else "Business documentary style video"}

Create a detailed, visual prompt that captures the emotion and meaning.
The image should be dramatic, high-quality, and suitable for a professional YouTube video.

IMPORTANT: Add these style keywords at the end: {AI_STYLE_KEYWORDS}

Return ONLY the prompt text, nothing else."""
)

assign_phase = lambda beat_index, total_beats: (
    "Hook" if beat_index < total_beats * 0.08 else
    "Context" if beat_index < total_beats * 0.25 else
    "Conflict" if beat_index < total_beats * 0.5 else
    "Pivot" if beat_index < total_beats * 0.75 else
    "Climax" if beat_index < total_beats * 0.9 else
    "Reveal"
)

def parse_json_response(response_text):
    cleaned = response_text.strip()
    if cleaned.startswith('```json'):
        cleaned = cleaned[7:]
    if cleaned.startswith('```'):
        cleaned = cleaned[3:]
    if cleaned.endswith('```'):
        cleaned = cleaned[:-3]
    try:
        return json.loads(cleaned.strip())
    except json.JSONDecodeError:
        print(f"       ⚠️  JSON Decode Error. Raw response: {cleaned[:100]}...")
        return []

def process_script(script_text):
    print("       ⏳ Segmenting script into beats...")
    beats_response = segment_script_to_beats(script_text)
    beats = parse_json_response(beats_response)
    
    if not beats:
        return []

    print(f"       📊 Processing {len(beats)} beats in batches of 10...")
    processed_beats = []
    
    batch_size = 10
    total_beats = len(beats)
    
    for i in range(0, total_beats, batch_size):
        batch = beats[i:i + batch_size]
        print(f"       🔄 Batch {i//batch_size + 1}: Processing beats {i+1}-{min(i+batch_size, total_beats)}...")
        
        try:
            analysis_response = analyze_beats_batch(batch)
            batch_analysis = parse_json_response(analysis_response)
            
            if len(batch_analysis) != len(batch):
                print(f"       ⚠️  Batch size mismatch (Sent {len(batch)}, Got {len(batch_analysis)}). Using fallback alignment.")
            
            for j, beat in enumerate(batch):
                if j < len(batch_analysis):
                    analysis = batch_analysis[j]
                else:
                    analysis = {
                        "beat": beat, "type": "abstract", 
                        "search_query": "", "meme_suggestion": None, "sfx": "transition"
                    }
                
                global_index = i + j
                phase = assign_phase(global_index, total_beats)
                sfx_category = analysis.get('sfx', 'transition').lower()
                sfx = SFX_MAPPINGS.get(sfx_category, "Swoosh, transition swoosh")
                
                beat_analysis_obj = {
                    "beat": beat,
                    "type": analysis.get('type', 'abstract'),
                    "search_query": analysis.get('search_query', ''),
                    "meme_suggestion": analysis.get('meme_suggestion'),
                    "person": None,
                    "brand": None,
                    "year": None, 
                    "is_abstract": analysis.get('type') == 'abstract'
                }

                processed_beats.append({
                    "index": global_index + 1,
                    "beat": beat,
                    "phase": phase,
                    "analysis": beat_analysis_obj,
                    "sfx": sfx
                })
                
        except Exception as e:
            print(f"       ❌ Error processing batch: {e}")
            for j, beat in enumerate(batch):
                global_index = i + j
                processed_beats.append({
                    "index": global_index + 1,
                    "beat": beat,
                    "phase": assign_phase(global_index, total_beats),
                    "analysis": {
                        "type": "abstract", "search_query": "", 
                        "meme_suggestion": None, "is_abstract": True
                    },
                    "sfx": "Swoosh, transition swoosh"
                })

    return processed_beats
