import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

generate_script = lambda topic, research_data: client.models.generate_content(
    model="gemini-2.0-flash",
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
).text
