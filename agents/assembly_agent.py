import os
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_text_clip(word, size=(720, 150), fontsize=80, color='white', stroke_color='black', stroke_width=3):
    """Creates a text image using Pillow and returns an RGBA numpy array."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arialbd.ttf", fontsize)
    except IOError:
        try:
            font = ImageFont.truetype("arial.ttf", fontsize)
        except IOError:
            font = ImageFont.load_default()

    try:
        bbox = d.textbbox((0, 0), word, font=font, stroke_width=stroke_width)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
    except AttributeError:
        w, h = d.textsize(word, font=font, stroke_width=stroke_width)

    position = ((size[0] - w) / 2, (size[1] - h) / 2)
    d.text(position, word, font=font, fill=color, stroke_width=stroke_width, stroke_fill=stroke_color)
    
    return np.array(img)

def assemble_video(audio_path, video_paths, subtitles, output_path="final_video.mp4"):
    """
    Assembles the final video by combining background clips, audio, and subtitles.
    """
    print("Loading audio...")
    audio_clip = AudioFileClip(audio_path)
    total_duration = audio_clip.duration
    
    print("Loading and preparing background video clips...")
    # Load videos
    clips = []
    for vp in video_paths:
        try:
            clip = VideoFileClip(vp)
            # Standardize resolution for 9:16 portrait (e.g., 720x1280)
            # Using resize from moviepy.video.fx.all isn't always directly imported cleanly, 
            # but clip.resize is available directly.
            clip = clip.resize(height=1280)
            clip = clip.crop(x1=clip.w/2 - 360, y1=0, x2=clip.w/2 + 360, y2=1280)
            
            # Mute background video
            clip = clip.without_audio()
            clips.append(clip)
        except Exception as e:
            print(f"Error loading clip {vp}: {e}")
            
    if not clips:
        raise ValueError("No valid video clips to assemble.")
        
    print("Concatenating background clips...")
    # Loop clips if they are shorter than audio duration
    combined_video = concatenate_videoclips(clips, method="compose")
    
    # If the combined video is shorter than audio, we loop it
    if combined_video.duration < total_duration:
        # loop is moviepy.video.fx.all.loop
        import moviepy.video.fx.all as vfx
        combined_video = combined_video.fx(vfx.loop, duration=total_duration)
    else:
        # Trim it to exact audio length
        combined_video = combined_video.subclip(0, total_duration)

    # Set the generated voiceover as the audio track
    combined_video = combined_video.set_audio(audio_clip)
    
    # Generate subtitles
    print("Generating subtitles...")
    subtitle_clips = []
    
    # TikTok style: one or a few words at a time.
    # We will just simple display the word exactly between start and end.
    # Note: Requires ImageMagick installed and configured for Moviepy.
    for sub in subtitles:
        word = sub["word"]
        start_t = sub["start"]
        end_t = sub["end"]
        
        # Add a tiny buffer so words don't completely disappear
        dur = end_t - start_t
        if dur < 0.1:
            dur = 0.1
            
        try:
            # Create text using PIL instead of ImageMagick
            img_array = create_text_clip(word, size=(720, 200), fontsize=80)
            
            # Separate RGB and Alpha channels for moviepy
            rgb_array = img_array[:, :, :3]
            alpha_array = img_array[:, :, 3] / 255.0
            
            txt_clip = ImageClip(rgb_array)
            mask_clip = ImageClip(alpha_array, ismask=True)
            txt_clip = txt_clip.set_mask(mask_clip)
            
            # Position at the center of the screen
            txt_clip = txt_clip.set_position(('center', 'center')).set_start(start_t).set_duration(dur)
            subtitle_clips.append(txt_clip)
        except Exception as e:
            print("Warning: Could not create subtitle image. Error:", e)
            break

    print("Compositing final video...")
    final_video = CompositeVideoClip([combined_video] + subtitle_clips)
    
    print(f"Exporting to {output_path}...")
    # Using ffmpeg preset ultrafast for quicker testing. For production, remove preset or use medium.
    final_video.write_videofile(
        output_path, 
        fps=30, 
        codec="libx264", 
        audio_codec="aac",
        preset="ultrafast",
        threads=4
    )
    
    print("Assembly complete!")
    return output_path

if __name__ == "__main__":
    pass

