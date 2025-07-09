# 🎨 Art Critic Bot

A brutally honest Discord bot that critiques your art using BLIP for image captioning and the Venice API for a philosophical commentary. Mention the bot and attach an image and it’ll reply with a brutally honest review.


## 🚀 What It Does

1. Listens for messages where it's mentioned
2. Describes the image using the `mistral-31-24b` venice model
3. Replies with a short, poetic, possibly painful critique

## 🛠 Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/venice-art-critic-bot.git
cd venice-art-critic-bot
```

2. Create a .env file
   
```env
DISCORD_TOKEN=your_discord_bot_token
VENICE_API_KEY=your_venice_api_key
```

You can get your Discord token from the Discord Developer Portal
The Venice API key is available at https://venice.ai

3. Install dependencies
If you're running locally or on Railway/Render with CPU-only PyTorch:

```bash
pip install -r requirements.txt
```

Your requirements.txt should look like:

```txt
discord.py
python-dotenv
requests
Pillow
```

4. Run the bot
   
```bash
python bot.py
```

📌 Usage

- Mention the bot in a message
- Attach an image

It will:
- Describe the image using BLIP
- Send the description to Venice AI
- Reply with a critique in the same channel

If you mention the bot but don’t attach an image, it will ask you to send one.
