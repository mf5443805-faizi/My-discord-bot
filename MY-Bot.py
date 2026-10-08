import os
import discord
from google import genai

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@client.event
async def on_ready():
    print(f'Bot online ho gaya hai: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.content
        )
        await message.channel.send(response.text)
    except Exception as e:
        await message.channel.send(f"Error details: {str(e)}")

client.run(os.getenv('DISCORD_TOKEN'))