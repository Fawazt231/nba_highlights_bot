import os
import sys
import praw
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
import time
import yt_dlp
from moviepy import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import shutil

def isPastDay(postTime: int):
    return time.time()-postTime <= 86400

def create_clean_directory(dir_path):
    # If the directory exists, remove it completely
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    # Recreate a clean, empty version of the directory
    os.makedirs(dir_path)

def run_main():
    # Authenticate with Reddit API
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )

    # Fetch top video posts from r/nba
    subreddit = reddit.subreddit("nba")
    #query = "flair:highlight OR flair:media"  # This helps filter posts tagged as highlights/media
    #posts = subreddit.search(query, sort="new", time_filter="day", limit=500)
    posts = subreddit.new(limit=10)
    #print(sum(1 for _ in posts))

    video_data = []
    for post in posts:
        if post.media and isPastDay(post.created_utc):
            if 'oembed' in post.media.keys():
                media_details = post.media['oembed']
                if post.link_flair_text == "Highlight":
                    video_data.append({
                        "title": post.title,
                        "url": post.url,
                        "upvotes": post.score
                    })
            if 'reddit_video' in post.media.keys():
                media_details = post.media['reddit_video']
                if post.link_flair_text == "Highlight":
                    video_data.append({
                        "title": post.title,
                        "url": post.url,
                        "upvotes": post.score
                })
    print(f"Found {len(video_data)} highlight posts.")

    # Directory to store downloaded clips
    DOWNLOAD_DIR = "nbaDownloads"
    
    create_clean_directory(DOWNLOAD_DIR)

    video_clips = []


    # Loop through video posts and download them
    for i, post in enumerate(video_data):
        url = post["url"]
        title = post["title"]
        
        # Generate a unique filename
        filename = f"{DOWNLOAD_DIR}/clip_{i}.mp4"
        
        print(f"⬇️ Downloading: {title}")

        try:
            # Set up yt_dlp options
            ydl_opts = {
                'outtmpl': filename,
                'quiet': True,
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',  # ensure .mp4
                'merge_output_format': 'mp4',
            }

            # Download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # Load the video using moviepy
            clip = VideoFileClip(filename, target_resolution=(1280,720))
            clip = process_clip(filename, title)  # Adjust keys accordingly
            # Optionally trim clips or resize here
            # e.g., clip = clip.subclip(0, min(10, clip.duration))  # First 10 sec

            video_clips.append(clip)

        except Exception as e:
            print(f"❌ Failed to process {url}: {e}")
            print(e.__traceback__)

    # Compile the clips into one video
    if video_clips:
        video_clips_small = video_clips[0:2] #small sample size of video clips
        print("🎬 Concatenating clips...")
        final_clip = concatenate_videoclips(video_clips_small, method="compose")
        final_clip.write_videofile(
            "highlight_compilation.mp4",
            codec="libx264",
            bitrate="5000k",
            preset="medium",
            audio_codec="aac",
            fps=30
        )
        print("✅ Compilation done: highlight_compilation.mp4")
    else:
        print("⚠️ No clips to compile.")


def process_clip(filepath, title, resolution_height=720):
    # Load clip
    clip = VideoFileClip(filepath, target_resolution=(1280,720))

    # Create a TextClip (bold, white text, centered)
    txt_clip = TextClip(
        text=title.lstrip("[Highlight] "),
        font=None,
        font_size=36,
        color='white',
        stroke_color="black",
        stroke_width=2,
        size=clip.size,
        method='caption',
        horizontal_align='left',
        vertical_align='bottom',
        duration=5
    )

    # Overlay text on top of the clip
    video_with_text = CompositeVideoClip([clip, txt_clip])
    
    return video_with_text





def small_sample():
    DOWNLOAD_DIR = "nbaDownloads"
    video_clips = []
    for i in range(0,1):
        filename = f"{DOWNLOAD_DIR}/clip_{i}.mp4"
        clip = VideoFileClip(filename, target_resolution=(1280,720))
        video_clips.append(clip)

    if video_clips:
        print("🎬 Concatenating clips...")
        final_clip = concatenate_videoclips(video_clips, method="compose")
        final_clip.write_videofile(
            "highlight_compilation_small.mp4",
            codec="libx264",
            bitrate="5000k",
            preset="medium",
            audio_codec="aac",
            fps=30
        )
        print("✅ Compilation done: highlight_compilation_small.mp4")
    else:
        print("⚠️ No clips to compile.")

def main():
    # print("running small sample")
    run_main()
main()