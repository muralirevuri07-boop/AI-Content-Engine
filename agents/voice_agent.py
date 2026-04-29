import os
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from dotenv import load_dotenv

load_dotenv()

elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=elevenlabs_api_key)

def generate_voiceover(text: str, output_path: str = "audio.mp3"):
    """
    Generates a voiceover for the given text using ElevenLabs and saves it to output_path.
    """
    try:
        # Generate audio using the ElevenLabs python client
        audio = client.generate(
            text=text,
            voice="Rachel", # You can change the voice here if you prefer
            model="eleven_multilingual_v2"
        )
        # Save the audio to a file
        save(audio, output_path)
        return output_path
    except Exception as e:
        print(f"Error generating voiceover: {e}")
        return None

if __name__ == "__main__":
    # Test voice agent
    generate_voiceover("Hello, this is a test of the ElevenLabs voice generation agent.", "test_audio.mp3")
