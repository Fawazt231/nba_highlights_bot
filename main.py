import praw
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
import time

def isPastDay(postTime: int):
    return time.time()-postTime <= 86400
    

# Authenticate with Reddit API
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

# Fetch top video posts from r/nba
subreddit = reddit.subreddit("nba")
#query = "flair:highlight OR flair:media"  # This helps filter posts tagged as highlights/media
#posts = subreddit.search(query, sort="new", time_filter="day", limit=100)
posts = subreddit.new(limit=200)
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
print(len(video_data))

    # if any(ext in post.url for ext in [".mp4", "streamable", "v.redd.it"]):  # Check if it's a video
    #     video_data.append({
    #         "title": post.title,
    #         "url": post.url,
    #         "upvotes": post.score
    #     })

# Print out the results
# for vid in video_data:
#     print(vid)



#print("Hello World")
