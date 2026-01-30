import os
import time
from google import genai
from google.genai import errors
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_script(topic, research_data):
    # Using 'models/gemini-flash-latest' as it appeared in the available models list
    # and might have better availability than specific versions
    model_name = "models/gemini-flash-latest" 
    
    try:
        print(f"  ...generating with {model_name}...")
        response = client.models.generate_content(
            model=model_name,
            contents=f"""You are a professional YouTube scriptwriter. Based on the following research about "{topic}", 
write a detailed, engaging 5-minute video script (approximately 750-1000 words).

The script should include:
1. An attention-grabbing hook (first 10 seconds)
2. Introduction of the topic
3. Main content with 3-5 key points
4. Examples and explanations
5. A strong call-to-action and outro

Research Data:
{research_data}

Write the script in a conversational, engaging tone suitable for YouTube. Include speaker directions in [brackets] where appropriate.
Format the script with clear sections."""
        )
        return response.text
    except errors.ClientError as e:
        if "429" in str(e):
            print("  ⚠️ Rate limit hit. Waiting 30 seconds before retrying...")
            time.sleep(30)
            print("  🔄 Retrying generation...")
            return client.models.generate_content(
                model=model_name,
                contents=f"Write a YouTube video script about {topic}."
            ).text
        raise e
