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

    # Try different models if one is experiencing high demand
    models_to_try = ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-3.5-flash']
    response_text = None
    last_error = None

    for model_name in models_to_try:
        try:
            response = gemini_client.models.generate_content(
                model=model_name,
                contents=message.content
            )
            response_text = response.text
            break # Agar response mil gaya toh loop break kar do
        except Exception as e:
            last_error = e
            continue

    if response_text:
        await message.channel.send(response_text)
    else:
        await message.channel.send(f"Error details: {str(last_error)}")

client.run(os.getenv('DISCORD_TOKEN'))