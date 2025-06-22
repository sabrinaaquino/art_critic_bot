import discord
import os
import requests
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
import base64

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
VENICE_API_KEY = os.getenv("VENICE_API_KEY")

# Initialize Discord client
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

# Load BLIP model + processor
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

def describe_image(image_bytes: bytes) -> str:
    """Generate a text description from an image using BLIP."""
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    inputs = processor(images=image, return_tensors="pt").to(device)
    out = model.generate(**inputs, max_new_tokens=50)
    return processor.decode(out[0], skip_special_tokens=True)

def send_to_venice(description: str) -> str:
    """Send the text prompt to Venice API and get critique."""
    payload = {
        "model": "venice-uncensored",
        "messages": [
            { "role": "system", "content": "You are a brutally honest art critic. Be bold, philosophical, and don't hold back. Be concise. A few sentences at most." },
            { "role": "user", "content": f"Critique this artwork based on the following description: '{description}'" }
        ],
        "venice_parameters": {
            "include_venice_system_prompt": False,
            "enable_web_search": "auto",
            "enable_web_citations": False
        }
    }

    headers = {
        "Authorization": f"Bearer {VENICE_API_KEY}",
        "Content-Type": "application/json"
    }

    res = requests.post("https://api.venice.ai/api/v1/chat/completions", json=payload, headers=headers)

    if res.status_code != 200:
        raise Exception(f"Venice API returned {res.status_code}: {res.text}")

    data = res.json()
    return data["choices"][0]["message"]["content"].strip()

@client.event
async def on_ready():
    print(f"🎨 Venice Art Critic is live as: {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith("image/"):
                try:
                    print(f"Image detected: {attachment.url}")
                    image_data = await attachment.read()
                    description = describe_image(image_data)
                    print(f"Description: {description}")
                    critique = send_to_venice(description)
                except Exception as e:
                    critique = f"Something went wrong: {e}"

                await message.reply(critique)
                break  # Handle only the first image

client.run(DISCORD_TOKEN)