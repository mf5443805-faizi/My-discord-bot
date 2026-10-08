import os
import discord
from google import genai

# Discord ke intents configure karein (message padhne ke liye zaroori hai)
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@client.event
async def on_ready():
    print(f'Bot online ho gaya hai: {client.user}')

@client.event
async def on_message(message):
    # Agar message khud bot ka bheja hua ho toh ignore karein taake loop na bane
    if message.author == client.user:
        return

    # User ka koi bhi message ho, seedha Gemini AI ko bhejein
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.content
        )
        await message.channel.send(response.text)
    except Exception as e:
        print(f"Error aa gaya: {e}")
        await message.channel.send("Maaf kijiye, AI response laane mein koi masla ho gaya hai.")

# Railway ki environment variable se token utha kar bot run karein
client.run(os.getenv('DISCORD_TOKEN'))