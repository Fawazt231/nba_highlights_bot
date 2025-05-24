import time
import tweepy
from config import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_BEARER_TOKEN
)

def post_video_to_twitter_v2(video_path, tweet_text):
        # OAuth 1.0a for media upload
    auth = tweepy.OAuth1UserHandler(
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET
    )
    api = tweepy.API(auth)

    # OAuth 2.0 Client for tweet creation
    client = tweepy.Client(
        bearer_token=TWITTER_BEARER_TOKEN,
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
    )

    retries = 3  # Number of retry attempts
    delay = 60  # Initial delay in seconds
    for attempt in range(retries):
        try:
            print(f"⬆️ Uploading video... (Attempt {attempt + 1}/{retries})")
            media = api.media_upload(video_path, media_category='tweet_video')
            print("✅ Media uploaded successfully.")

            # Posting the tweet with media
            response = client.create_tweet(text=tweet_text, media_ids=[media.media_id])
            print("✅ Tweet posted successfully:", response.data)
            return "SUCCESS" # Exit the loop and finish if the tweet is successful

        except Exception as e:
            #TODO: is it failing becase of video source?

            print(f"❌ Failed to post tweet on attempt {attempt + 1}: {e}")
            # Log the error details to understand more
            print(f"Error details: {e}")

            # Retry only if not the last attempt
            if attempt < retries - 1:
                print(f"⏳ Retrying in {delay} seconds...")
                time.sleep(delay)  # Exponential backoff logic
                delay *= 2  # Double the delay for the next retry

# post_video_to_twitter_v2("nbaDownloads/clip_1.mp4", "[Highlight] Technical foul called on Draymond after elbow to the face of Naz Reid -- his fifth of the playoffs")