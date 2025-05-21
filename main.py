import os
import sys
import praw
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
import time
import yt_dlp
from moviepy import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import shutil
from supabaseUtils import already_uploaded, mark_as_uploaded
from twitter_bot import post_video_to_twitter_v2
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

DOWNLOAD_DIR = "nbaDownloads"

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

    # Directory to store downloaded clips    
    create_clean_directory(DOWNLOAD_DIR)

    # Fetch top video posts from r/nba
    subreddit = reddit.subreddit("nba")
    logging.info("Querying subreddit")
    posts = subreddit.new(limit=20)

    video_data = []
    for post in posts:
        if post.media and isPastDay(post.created_utc):
            if 'oembed' in post.media.keys():
                media_details = post.media['oembed']
                if post.link_flair_text == "Highlight":
                    video_data.append({
                        "title": post.title,
                        "url": post.url,
                        "upvotes": post.score,
                        "id": post.id
                    })
            if 'reddit_video' in post.media.keys():
                media_details = post.media['reddit_video']
                if post.link_flair_text == "Highlight":
                    video_data.append({
                        "title": post.title,
                        "url": post.url,
                        "upvotes": post.score,
                        "id": post.id
                })
    logging.info(f"Found {len(video_data)} highlight posts.")

    video_clips = []


    # Loop through video posts and download them
    for i, post in enumerate(video_data):
        reddit_post_id = post["id"]
        url = post["url"]
        title = post["title"]
        if already_uploaded(reddit_post_id):
            logging.info(f"Post \"{title}\" is already uploaded")
            continue
        
        # Generate a unique filename
        filename = f"{DOWNLOAD_DIR}/clip_{i}.mp4"
        
        logging.info(f"⬇️ Downloading: {title}")

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
            clip = process_clip(filename, title, i, reddit_post_id)  # Adjust keys accordingly
            # Optionally trim clips or resize here
            # e.g., clip = clip.subclip(0, min(10, clip.duration))  # First 10 sec
        except Exception as e:
            logging.info(f"❌ Failed to process {url}: {e}")
            logging.info(e.__traceback__)


def process_clip(filepath, post_title, idx, post_id, resolution_height=720):
    # Load clip
    clip = VideoFileClip(filepath, target_resolution=(1280,720))
    if clip.duration > 140:
        return
    
    fileName = f"{DOWNLOAD_DIR}/highlight_{idx}.mp4"
    tweetTitle = post_title.lstrip("[Highlight] ")

    # Create a TextClip (bold, white text, centered)
    txt_clip = TextClip(
        text=tweetTitle,
        font='Arial',
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
    
    video_with_text.write_videofile(
        fileName,
        codec="libx264",
        bitrate="5000k",
        preset="medium",
        audio_codec="aac",
        fps=30
    )

    post_video_to_twitter_v2(fileName, tweetTitle)
    mark_as_uploaded(post_id, post_title)
    time.sleep(60)

    return video_with_text

def main():
    # print("running small sample")
    run_main()

if __name__ == "__main__":
    main()