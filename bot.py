import os
import base64
import requests
import discord
import torch
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from transformers import BlipProcessor, BlipForConditionalGeneration

# === Load environment ===
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
VENICE_API_KEY = os.getenv("VENICE_API_KEY")

# === Set up Discord client ===
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

# === Load BLIP model and processor ===
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

# === Image description ===
def describe_image(image_bytes: bytes) -> str:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    inputs = processor(images=image, return_tensors="pt").to(device)
    output = model.generate(**inputs, max_new_tokens=50)
    return processor.decode(output[0], skip_special_tokens=True)

# === Venice API call ===
def send_to_venice(description: str) -> str:
    url = "https://api.venice.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {VENICE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "venice-uncensored",
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
                "content": f"Critique this artwork based on the following description: '{description}'"
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
                    image_bytes = await attachment.read()
                    description = describe_image(image_bytes)
                    print(f"Generated description: {description}")
                    critique = send_to_venice(description)
                except Exception as e:
                    critique = f"Something went wrong: {e}"

                await message.reply(critique)
                return

        # If bot was mentioned but no image was found
        await message.reply("Please attach an image you'd like me to critique.")

# === Run bot ===
client.run(DISCORD_TOKEN)