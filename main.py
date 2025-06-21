from fastapi import FastAPI
from twitter_client import get_my_username
import time
from twitter_client import get_mentions, extract_tweet_id, download_image_from_tweet, reply_to_tweet

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.get("/whoami")
def whoami():
    username = get_my_username()
    return {"twitter_handle": username}

latest_id = None

@app.get("/run-critic/")
def run_critic():
    global latest_id

    while True:
        mentions = get_mentions(since_id=latest_id)
        for tweet in reversed(mentions):
            tweet_id = tweet.id
            if "media" in tweet.entities:
                img, username = download_image_from_tweet(str(tweet_id))
                if img:
                    # Placeholder opinion
                    opinion = f"Ah, {username}... bold choice of lighting. Daringly mid."
                    reply_to_tweet(opinion, tweet_id)
            latest_id = max(latest_id or 0, tweet.id)

        time.sleep(15)
