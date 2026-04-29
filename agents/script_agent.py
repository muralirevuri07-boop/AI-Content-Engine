import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_script_and_keywords(topic: str):
    """
    Generates a 30-second script and visual keywords for a given topic.
    Returns a dictionary with 'script' (string) and 'keywords' (list of strings).
    """
    system_prompt = '''You are an expert short-form video scriptwriter (TikTok, Instagram Reels, YouTube Shorts).
Your goal is to write a highly engaging, fast-paced script that takes exactly 30 seconds to read (about 65-80 words).
Ensure the script starts with a strong hook.

In addition to the script, provide 3 to 5 highly descriptive visual keywords or short phrases.
These keywords will be used to search a stock video site (like Pexels) for background footage.
The visual keywords should be generic enough to find stock video but relevant to the topic. For example: "coding on laptop", "futuristic AI network", "dark hacker room".

You must respond in exactly this JSON format:
{
  "script": "The actual spoken text goes here...",
  "keywords": ["keyword 1", "keyword 2", "keyword 3"]
}'''

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # You could change this to gpt-4o for better quality depending on preference
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Topic: {topic}"}
        ],
        response_format={"type": "json_object"}
    )

    try:
        content = response.choices[0].message.content
        result = json.loads(content)
        return result
    except Exception as e:
        print(f"Error parsing script: {e}")
        # Fallback
        return {
            "script": "System failure. Could not generate script.",
            "keywords": ["error", "blank screen"]
        }

if __name__ == "__main__":
    # Test script agent
    res = generate_script_and_keywords("The history of artificial intelligence")
    print(res)
