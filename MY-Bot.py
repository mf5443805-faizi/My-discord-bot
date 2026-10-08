import os
import discord
from google import genai

# Discord intents setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Modern Gemini AI Client setup
# Modern Gemini AI Client setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

@client.event
async def on_ready():
    print(f'Bot successfully online ho gaya hai: {client.user}')

@client.event
async def on_message(message):
    # Bot ke apne messages ko ignore karein
    if message.author == client.user:
        return

    # Simple command: !hello
    if message.content.startswith('!hello'):
        await message.channel.send('Salam! Main bilkul theek kaam kar raha hoon. 🚀')

    # Gemini AI command: !ai <aap ka sawal>
    if message.content.startswith('!ai '):
        query = message.content[4:]
        if not genai_client:
            await message.channel.send("Error: Railway mein GEMINI_API_KEY set nahi hai!")
            return
        
        try:
            # Modern Gemini API call (gemini-2.5-flash ya gemini-2.0-flash)
            response = genai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=query,
            )
            await message.channel.send(response.text)
        except Exception as e:
            await message.channel.send(f"Gemini response dene mein masla hua: {e}")

# Securely run bot using Railway environment variable
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    print("Error: DISCORD_TOKEN environment variable nahi mila!")
else:
    client.run(TOKEN)