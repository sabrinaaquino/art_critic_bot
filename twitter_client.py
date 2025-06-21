import tweepy
import os
from dotenv import load_dotenv
from PIL import Image
import requests
from io import BytesIO

# Load environment variables
load_dotenv()

# Setup authentication
auth = tweepy.OAuth1UserHandler(
    os.getenv("TWITTER_API_KEY"),
    os.getenv("TWITTER_API_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_SECRET"),
)

# Create Twitter API client
twitter = tweepy.API(auth)

# Verify account
def get_my_username():
    try:
        user = twitter.verify_credentials()
        if user:
            return user.screen_name
        else:
            return "Could not verify credentials"
    except Exception as e:
        return f"Error: {str(e)}"

# Fetch tweet by ID
def get_tweet(tweet_id):
    return twitter.get_status(tweet_id, tweet_mode="extended")

# Reply to tweet (with or without image)
def reply_to_tweet(text, tweet_id, media_path=None):
    if media_path:
        media = twitter.media_upload(media_path)
        return twitter.update_status(
            status=text,
            in_reply_to_status_id=tweet_id,
            auto_populate_reply_metadata=True,
            media_ids=[media.media_id]
        )
    else:
        return twitter.update_status(
            status=text,
            in_reply_to_status_id=tweet_id,
            auto_populate_reply_metadata=True
        )

def get_mentions(since_id=None):
    mentions = twitter.mentions_timeline(since_id=since_id, tweet_mode="extended")
    return mentions

def extract_tweet_id(tweet_url: str) -> str:
    return tweet_url.strip("/").split("/")[-1]

def download_image_from_tweet(tweet_id: str):
    tweet = twitter.get_status(tweet_id, tweet_mode="extended")
    media = tweet.entities.get("media", [])
    if not media:
        return None, tweet.user.screen_name
    image_url = media[0]["media_url_https"]
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    return img, tweet.user.screen_name
