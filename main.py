import os
import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN_DISCORD")

URL_TERRAQUAKEAPI_RECENT = "https://api.terraquakeapi.com/v1/earthquakes/recent"
URL_TERRAQUAKEAPI_TODAY = "https://api.terraquakeapi.com/v1/earthquakes/today"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)


@bot.event
async def on_ready():
    print(f"Earthquake bot started! {bot.user}")

    channel_id = 1417776031149981707
    channel = bot.get_channel(channel_id)

    if channel:
        await channel.send(
            "🌍 Earthquake Bot is online!\nType `$info` to see available commands."
        )
        

@bot.command()
async def info(ctx):
    message = """
        🌍 **Earthquake Bot - Guide**

        This bot allows you to get information about recent earthquakes.

        📌 **Available commands:**

        ➡️ `$earthquake recent limit <number>`
        Returns the latest N earthquake events
        Example: `$earthquake recent limit 5`
        
        ➡️ `$earthquake today limit <number>`
        Returns the latest N earthquakes recorded today
        Example: `$earthquake today limit 10`

        ➡️ `$test <text>`
        Repeats the input message
        Example: `$test hello`

        ➡️ `$info`
        Displays this guide

        ⚙️ **Data source:**
        TerraQuake API (real-time seismic events) - terraquakeapi.com -

        """
    await ctx.send(message)


@bot.command()
async def earthquake(ctx, *args):
    try:
        if len(args) != 3:
            await ctx.send("Usage: $earthquake recent limit 10")
            return

        mode = args[0]
        keyword = args[1]
        limit = int(args[2])
        
        if keyword != "limit":
            await ctx.send("Usage: $earthquake recent limit 10")
            return
        
        if mode == 'recent':
            url = URL_TERRAQUAKEAPI_RECENT
        elif mode == 'today':
            url = URL_TERRAQUAKEAPI_TODAY
        else:
            await ctx.send("Invalid mode. Use recent or today")
            return
    
        response = requests.get(f"{url}?limit={limit}", timeout=10)
        
        if response.status_code != 200:
            await ctx.send("API request error.")
            return

        data = response.json()

        # Debug struttura
        print("TYPE:", type(data))
        print("DATA:", data)

        if (
            data.get("success")
            and "payload" in data
            and isinstance(data["payload"], list)
        ):
            await ctx.send(f"{mode} seismic events:")
            if len(data["payload"]) > 0:
                for event in data["payload"]:
                    props = event.get("properties", {})
                    magnitude = props.get("mag", "N/A")
                    magType = props.get("magType")
                    place = props.get("place", "Unknown")
                    time = props.get("time")
                    print(f"{magnitude}{magType} - {place} - {time}")
                    await ctx.send(f"{magnitude}{magType} - {place} - {time}")
            else:
                await ctx.send("No earthquake data found.")
                print("No earthquake data found.")

    except Exception as error:
        await ctx.send("Earthquakes endpoint request error.")
        print(f"Error: {error}")


@bot.command()
async def test(ctx, *args):
    response = " ".join(args)
    await ctx.send(response)


@bot.command()
async def clear(ctx):
    await ctx.channel.purge()
    await ctx.send("Messages deleted!", delete_after=3)


bot.run(token)
