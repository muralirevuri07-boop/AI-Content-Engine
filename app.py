import streamlit as st
import os

from agents.script_agent import generate_script_and_keywords
from agents.voice_agent import generate_voiceover
from agents.subtitle_agent import generate_subtitles
from agents.video_agent import fetch_and_download_videos
from agents.assembly_agent import assemble_video

from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Short-Form Video Generator", page_icon="🎥", layout="centered")

st.title("🎥 AI Multi-Agent Video Generator")
st.write("Generate a 30-second short-form video from a single topic.")

# Check for API keys
openai_key = os.getenv("OPENAI_API_KEY")
elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
pexels_key = os.getenv("PEXELS_API_KEY")

missing_keys = []
if not openai_key or openai_key == "your_openai_api_key_here":
    missing_keys.append("OpenAI (OPENAI_API_KEY)")
if not elevenlabs_key or elevenlabs_key == "your_elevenlabs_api_key_here":
    missing_keys.append("ElevenLabs (ELEVENLABS_API_KEY)")
if not pexels_key or pexels_key == "your_pexels_api_key_here":
    missing_keys.append("Pexels (PEXELS_API_KEY)")
    
if missing_keys:
    st.warning(f"⚠️ Missing API Keys in .env file: {', '.join(missing_keys)}")
    st.info("Please update the .env file with your valid keys before generating videos.")

topic = st.text_input("Enter a topic for your video:", placeholder="e.g., The History of Artificial Intelligence")

if st.button("Generate Video", type="primary", disabled=bool(missing_keys)):
    if not topic.strip():
        st.error("Please enter a topic.")
    else:
        try:
            # Create progress indicators
            with st.status("Starting Generation Pipeline...", expanded=True) as status:
                
                # 1. Script Generation
                st.write("📝 Agent 1: Generating Script and Visual Keywords...")
                script_data = generate_script_and_keywords(topic)
                script_text = script_data.get("script", "")
                keywords = script_data.get("keywords", [])
                st.success(f"Script generated! ({len(script_text.split())} words)")
                with st.expander("View Script & Keywords"):
                    st.write("**Script:**", script_text)
                    st.write("**Keywords:**", ", ".join(keywords))
                    
                # 2. Voice Generation
                st.write("🎙️ Agent 2: Synthesizing Voiceover...")
                audio_path = generate_voiceover(script_text, "temp_audio.mp3")
                if not audio_path:
                    raise Exception("Failed to generate voiceover.")
                st.success("Audio generated!")
                
                # 3. Subtitle Generation
                st.write("✍️ Agent 3: Generating precision word-level subtitles...")
                subtitles = generate_subtitles(audio_path)
                st.success(f"Subtitles mapped! ({len(subtitles)} parts)")
                
                # 4. Video Fetching
                st.write("🎬 Agent 4: Searching and downloading stock footage...")
                video_paths = fetch_and_download_videos(keywords, output_dir="clips", num_clips=3)
                if not video_paths:
                    raise Exception("Failed to download any background videos. The Pexels API might be rate limited or invalid.")
                st.success(f"Downloaded {len(video_paths)} video clips!")
                
                # 5. Final Assembly
                st.write("🎞️ Agent 5: Assembling final video track...")
                final_output_path = "final_output.mp4"
                assemble_video(audio_path, video_paths, subtitles, output_path=final_output_path)
                st.success("Video assembled successfully!")
                
                status.update(label="Generation Complete!", state="complete", expanded=False)
                
            st.balloons()
            
            # Display Result
            st.subheader("Your AI Generated Video")
            
            # Show video in UI
            st.video(final_output_path)
            
            # Download button
            with open(final_output_path, "rb") as file:
                btn = st.download_button(
                    label="Download Video",
                    data=file,
                    file_name=f"{topic.replace(' ', '_')}_short.mp4",
                    mime="video/mp4"
                )
                
        except Exception as e:
            st.error(f"An error occurred during generation: {str(e)}")
            import traceback
            st.expander("Error Details").text(traceback.format_exc())

# Add some instructions or footer
st.markdown("---")
st.caption("Powered by OpenAI, ElevenLabs, Faster-Whisper, and Pexels. Built with Streamlit and MoviePy.")
