import discord
import requests
import pandas as pd
import matplotlib.pyplot as plt
import io
import google.generativeai as genai

# ==========================================
# --- CONFIGURATION & API KEYS ---
# ==========================================
DISCORD_TOKEN = "MTU1NzA2NDk3MDAzMjY0ODE5Mw.Gr5jOF.ISOgdeyp_ef0lWChhUTGsY_7GzZd1M-t--i6z0"
GEMINI_API_KEY = "AQ.Ab8RN6JvKxR7-iqxXZvYPxO0VdsLROUm-PXSlKziy59tKXI-Sg"

# Initialize Google Gemini API
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-3.5-flash")

# Setup Discord Client with Message Content Intent
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

current_update_time = "7:00"  

@client.event
async def on_ready():
    print(f"Logged in as {client.user.name} (ID: {client.user.id})")
    print("AI Crypto & Coding Management Bot is online and ready (Prefix-Free)!")

@client.event
async def on_message(message):
    # Bot ko khud apne hi messages ka jawab dene se rokne ke liye
    if message.author == client.user:
        return

    content = message.content.strip()

    # 1. LIVE CRYPTO PRICE (Misal: price bitcoin)
    if content.lower().startswith("price "):
        coin = content.split(" ")[1].lower()
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd,pkr"
            response = requests.get(url)
            data = response.json()
            
            if coin in data:
                usd_price = data[coin]['usd']
                pkr_price = data[coin]['pkr']
                await message.channel.send(f"📊 **{coin.upper()} Live Rate**:\n💵 USD: ${usd_price}\n🇵🇰 PKR: ₨{pkr_price}")
            else:
                await message.channel.send(f"❌ '{coin}' nahi mila. Sahi coin name likhein (jaise: price bitcoin).")
        except Exception as e:
            await message.channel.send(f"❌ Error fetching price: {e}")
        return

    # 2. REAL-TIME GRAPH (Misal: graph bitcoin)
    elif content.lower().startswith("graph "):
        coin = content.split(" ")[1].lower()
        async with message.channel.typing():
            try:
                url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days=7"
                response = requests.get(url)
                data = response.json()
                
                if "prices" not in data:
                    await message.channel.send(f"❌ '{coin}' ka data nahi mil saka. Sahi naam likhein.")
                    return
                
                prices = data["prices"]
                df = pd.DataFrame(prices, columns=["Timestamp", "Price"])
                df["Date"] = pd.to_datetime(df["Timestamp"], unit="ms")
                
                plt.figure(figsize=(10, 5))
                plt.plot(df["Date"], df["Price"], color="#00ffcc", linewidth=2, label=f"{coin.capitalize()} Price")
                plt.title(f"{coin.upper()} - Last 7 Days Price Trend", fontsize=14, color="white")
                plt.xlabel("Date", fontsize=10, color="white")
                plt.ylabel("Price in USD ($)", fontsize=10, color="white")
                plt.grid(True, linestyle="--", alpha=0.3)
                
                plt.gca().set_facecolor("#2f3136")
                plt.gcf().patch.set_facecolor("#2f3136")
                plt.tick_params(colors="white", which="both")
                plt.legend()
                plt.tight_layout()
                
                image_binary = io.BytesIO()
                plt.savefig(image_binary, format="png", facecolor=plt.gcf().get_facecolor(), edgecolor='none')
                image_binary.seek(0)
                plt.close()
                
                file = discord.File(fp=image_binary, filename=f"{coin}_graph.png")
                await message.channel.send(content=f"📈 **{coin.upper()} ka Pichle 7 Dino ka Real-Time Graph:**", file=file)
                
            except Exception as e:
                await message.channel.send(f"❌ Graph banane mein error aa gaya: {e}")
        return

    # 3. SET TIME COMMAND (Misal: settime 8:00)
    elif content.lower().startswith("settime "):
        global current_update_time
        new_time = content.split(" ")[1]
        current_update_time = new_time
        await message.channel.send(f"✅ Success! **{message.author.name}** ne update ka time change karke **{new_time}** kar diya hai.")
        return

    # 4. GENERAL AI CHAT (Har aam message ka seedha Gemini AI se jawab)
    else:
        async with message.channel.typing():
            try:
                full_prompt = (
                    "You are a helpful AI assistant specialized in coding, crypto analysis, "
                    f"and general technical problem solving.\nUser question: {content}"
                )
                response = gemini_model.generate_content(full_prompt)
                answer = response.text
                
                if len(answer) > 2000:
                    answer = answer[:1990] + "..."
                    
                await message.channel.send(f"🤖 **Gemini AI Assistant**:\n{answer}")
            except Exception as e:
                await message.channel.send(f"❌ Gemini AI se rabta karne mein masla aa raha hai: {e}")

# Run the Bot
if __name__ == "__main__":
    client.run(DISCORD_TOKEN)