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

@client.event
async def on_ready():
    print(f'Bot online ho gaya hai: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    channel_id = message.channel.id

    # Agar is channel ka pehle se chat session nahi hai, toh naya bana lo (Memory start)
    if channel_id not in channel_chats:
        try:
            channel_chats[channel_id] = gemini_client.chats.create(model='gemini-2.5-flash')
        except Exception as e:
            await message.channel.send(f"Error initializing chat: {str(e)}")
            return

    chat_session = channel_chats[channel_id]

    try:
        # Chat session ke zariye message bhejna taake purani baatein yaad rahein
        response = chat_session.send_message(message.content)
        response_text = response.text

        if response_text:
            # Agar message 2000 characters se lamba ho toh split karke bhejein
            if len(response_text) > 2000:
                for i in range(0, len(response_text), 2000):
                    await message.channel.send(response_text[i:i+2000])
            else:
                await message.channel.send(response_text)
                
    except Exception as e:
        # Agar quota ya koi aur error aaye toh user ko bata do
        await message.channel.send(f"Error details: {str(e)}")

client.run(os.getenv('DISCORD_TOKEN'))