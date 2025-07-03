import os
import base64
import requests
import discord
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

# === Load environment ===
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
VENICE_API_KEY = os.getenv("VENICE_API_KEY")

# === Set up Discord client ===
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

# === Venice API call with image ===
def send_image_to_venice(image_bytes: bytes, user_message: str = "") -> str:
    url = "https://api.venice.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {VENICE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Convert image to base64
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    # Clean up user message (remove bot mention)
    clean_message = user_message.replace(f'<@{client.user.id}>', '').strip()

    # Create the text prompt based on user input
    if clean_message:
        text_prompt = f"User says: '{clean_message}'. Please critique this artwork accordingly. Be brutally honest and philosophical."
    else:
        text_prompt = "Critique this artwork. Be brutally honest and philosophical."
    
    
    payload = {
        "model": "mistral-31-24b",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a brutally honest art critic. Be bold, philosophical, and don't hold back. "
                    "Be concise. A few sentences at most."
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "venice_parameters": {
            "include_venice_system_prompt": False,
            "enable_web_search": "auto",
            "enable_web_citations": False
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()

# === Event handlers ===
@client.event
async def on_ready():
    print(f"🎨 Venice Art Critic is live as: {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if client.user in message.mentions:
        # If there are image attachments, try to process them
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith("image/"):
                try:
                    print(f"Image detected: {attachment.url}")
                    print(f"User message: {message.content}")
                    image_bytes = await attachment.read()
                    critique = send_image_to_venice(image_bytes, message.content)
                except Exception as e:
                    critique = f"Something went wrong: {e}"

                await message.reply(critique)
                return

        # If bot was mentioned but no image was found
        await message.reply("Please attach an image you'd like me to critique.")

# === Run bot ===
client.run(DISCORD_TOKEN)