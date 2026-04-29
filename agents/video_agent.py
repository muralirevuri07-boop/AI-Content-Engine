import os
import requests
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def fetch_and_download_videos(keywords, output_dir="clips", num_clips=3):
    """
    Searches Pexels for vertical videos using the provided keywords.
    Downloads them to the output_dir.
    Returns a list of downloaded video paths.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    headers = {
        "Authorization": PEXELS_API_KEY
    }
    
    downloaded_paths = []
    
    # We will try to download one clip per keyword until we reach num_clips limit
    clip_count = 0
    for keyword in keywords:
        if clip_count >= num_clips:
            break
            
        print(f"Searching Pexels for video matching: {keyword}")
        # search for vertical videos (orientation=portrait)
        url = f"https://api.pexels.com/videos/search?query={keyword}&orientation=portrait&per_page=3"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            videos = data.get("videos", [])
            
            if videos:
                # pick the first video result
                video = videos[0]
                
                # find an hd resolution standard (e.g., 720x1280 or 1080x1920)
                video_files = video.get("video_files", [])
                
                # Sort by resolution (prefer HD) or just pick highest quality
                # But since it's vertical, we look for width < height
                valid_files = [f for f in video_files if f.get('width') and f.get('height') and f['width'] < f['height']]
                
                if valid_files:
                    # Pick a reasonable quality to avoid huge downloads for testing
                    # Sort by width, grab something around 720p or 1080p width
                    valid_files.sort(key=lambda x: x['width'], reverse=True)
                    best_file = valid_files[0]
                    download_link = best_file.get("link")
                    
                    if download_link:
                        print(f"Downloading video for keyword '{keyword}'...")
                        vid_resp = requests.get(download_link, stream=True)
                        if vid_resp.status_code == 200:
                            save_path = os.path.join(output_dir, f"clip_{clip_count}.mp4")
                            with open(save_path, 'wb') as f:
                                for chunk in vid_resp.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            downloaded_paths.append(save_path)
                            clip_count += 1
                else:
                    print(f"No suitable vertical resolution found for '{keyword}'")
            else:
                print(f"No videos found for keyword: {keyword}")
        else:
            print(f"Pexels API Error: {response.status_code} - {response.text}")
            
    print(f"Total downloaded clips: {len(downloaded_paths)}")
    return downloaded_paths

if __name__ == "__main__":
    # Test video agent
    paths = fetch_and_download_videos(["hacker space", "cyber security"], output_dir="temp_clips")
    print("Downloaded:", paths)
