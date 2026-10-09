import os
import discord
from google import genai
from google.genai import types

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Channel-wise chat sessions store karne ke liye dictionary (Memory)
channel_chats = {}

# Try karne ke liye models ki list
MODELS_TO_TRY = ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-3.5-flash']

@client.event
async def on_ready():
    print(f'Bot online ho gaya hai: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    channel_id = message.channel.id
    response_text = None
    last_error = None

    # Safety settings
    safety_settings = [
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
    ]

    for model_name in MODELS_TO_TRY:
        try:
            if channel_id not in channel_chats:
                channel_chats[channel_id] = gemini_client.chats.create(
                    model=model_name,
                    config=types.GenerateContentConfig(safety_settings=safety_settings)
                )
            
            chat_session = channel_chats[channel_id]
            response = chat_session.send_message(message.content)
            
            if response and response.text:
                response_text = response.text
                break
        except Exception as e:
            last_error = e
            if channel_id in channel_chats:
                del channel_chats[channel_id]
            continue

    if response_text:
        # Limit ko 5000 characters tak extend kar diya gaya hai (Discord ki limit ki wajah se ye tukron mein jaye ga)
        max_length = 5000
        # Agar jawab lamba ho toh usay safe chunks mein split karke bhejein (har chunk max 2000 characters ka hoga taake Discord accept kare)
        for i in range(0, min(len(response_text), max_length), 2000):
            await message.channel.send(response_text[i:i+2000])
    else:
        await message.channel.send(f"Error details: {str(last_error)}")

client.run(os.getenv('DISCORD_TOKEN'))