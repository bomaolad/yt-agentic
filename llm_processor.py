from google import genai
from google.genai import errors
import json
import time
import random
from config import GEMINI_API_KEY, BEAT_LENGTH_MIN, BEAT_LENGTH_MAX, PHASES, AI_STYLE_KEYWORDS, SFX_MAPPINGS

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = 'models/gemini-2.0-flash-lite'

def generate_content(prompt, retries=10, initial_delay=5.0):
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            return response.text.strip()
        except errors.ClientError as e:
            if e.code == 429:
                if attempt == retries - 1:
                    raise  # Re-raise if max retries reached
                
                # Exponential backoff with jitter: 2s, 4s, 8s, 16s + random jitter
                sleep_time = (initial_delay * (2 ** attempt)) + random.uniform(0.1, 1.0)
                print(f"       ⚠️  Rate limit hit (429). Waiting {sleep_time:.1f}s before retry {attempt + 1}/{retries}...")
                time.sleep(sleep_time)
            else:
                raise  # Re-raise other errors immediately
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
    
    # Process in batches of 10
    batch_size = 10
    total_beats = len(beats)
    
    for i in range(0, total_beats, batch_size):
        batch = beats[i:i + batch_size]
        print(f"       🔄 Batch {i//batch_size + 1}: Processing beats {i+1}-{min(i+batch_size, total_beats)}...")
        
        try:
            analysis_response = analyze_beats_batch(batch)
            batch_analysis = parse_json_response(analysis_response)
            
            # Ensure we have analysis for each beat, even if LLM messes up count
            # Map by index or matching text ideally, but simple zip for now
            # Fallback for mismatches
            if len(batch_analysis) != len(batch):
                print(f"       ⚠️  Batch size mismatch (Sent {len(batch)}, Got {len(batch_analysis)}). Using fallback alignment.")
            
            for j, beat in enumerate(batch):
                # Safely get analysis or default
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
                
                # Reconstruct the singular analysis object structure expected by main.py
                beat_analysis_obj = {
                    "beat": beat,
                    "type": analysis.get('type', 'abstract'),
                    "search_query": analysis.get('search_query', ''),
                    "meme_suggestion": analysis.get('meme_suggestion'),
                    "person": None, # Simplification for batching
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
            # Fallback for entire failed batch
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
