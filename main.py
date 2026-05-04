import os
import discord
from discord.ext import commands
import difflib
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN_DISCORD")

URL_TERRAQUAKEAPI_RECENT = "https://api.terraquakeapi.com/v1/earthquakes/recent"
URL_TERRAQUAKEAPI_TODAY = "https://api.terraquakeapi.com/v1/earthquakes/today"
URL_TERRAQUAKEAPI_LAST_WEEK = "https://api.terraquakeapi.com/v1/earthquakes/last-week"
URL_TERRAQUAKEAPI_REGION = "https://api.terraquakeapi.com/v1/earthquakes/region"

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
        This endpoint retrieves all recent seismic events from the beginning of the year until today via the TerraQuake API sorted from the most recent to the least recent.
        Returns the latest N earthquake events
        Example: `$earthquake recent limit 5`
        
        ➡️ `$earthquake today limit <number>`
        This endpoint retrieves all seismic events that occurred today (from 00:00 UTC to the current time) from the TerraQuake API.
        Returns the latest N earthquakes recorded today
        Example: `$earthquake today limit 10`
        
        ➡️ `$earthquake last-week limit <number>`
        This endpoint retrieves all seismic events that occurred in the last 7 days from the TerraQuake API.
        Returns the latest N earthquakes recorded last-week
        Example: `$earthquake last-week limit 10`
        
        ➡️ `$earthquake region Calabria limit <number>`
        This endpoint retrieves all seismic events that occurred within a specific Italian region from the TerraQuake API, from the start of the current year up to today.
        Returns the latest N earthquakes recorded region
        Example: `$earthquake region Calabria limit 10`

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
        if len(args) < 3:
            await ctx.send("Usage: $earthquake (recent or today or last-week or region) limit 10")
            return

        mode = args[0]
        
        if mode == "region":
            keyword = args[1]
            limit = int(args[3])
            url = f"{URL_TERRAQUAKEAPI_REGION}?region={keyword}&limit={limit}"
            await ctx.send(f"{mode} {keyword} seismic events:")
            
        else:
            keyword = args[1]
            limit = int(args[2])
            
            if keyword != "limit":
                await ctx.send("Usage: $earthquake (recent or today or last-week) limit 10")
                return
            
            if mode == "recent":
                url = f"{URL_TERRAQUAKEAPI_RECENT}?limit={limit}"
                await ctx.send(f"{mode} seismic events:")
                
            elif mode == "today":
                url = URL_TERRAQUAKEAPI_TODAY
                await ctx.send(f"{mode} seismic events:")
                
            elif mode == "last-week":
                url = f"{URL_TERRAQUAKEAPI_LAST_WEEK}?limit={limit}"
                await ctx.send(f"{mode} seismic events:")
                
            else:
                await ctx.send("Invalid mode. Use recent or today or last-week")
                return
        
        response = requests.get(url, timeout = 10)
        # response = requests.get(f"{url}?limit={limit}", timeout=10)
        
        
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
            if len(data["payload"]) > 0:
                for event in data["payload"]:
                    props = event.get("properties", {})
                    magnitude = props.get("mag", "N/A")
                    magType = props.get("magType")
                    place = props.get("place", "Unknown")
                    time = props.get("time")
                    
                    if time:
                        dt = datetime.fromisoformat(time)
                        formatted_time = dt.strftime("%d/%m/%Y %H:%M")
                    else:
                        formatted_time = "N/A"

                    print("")
                    print(f"{magnitude}{magType} - {place} - {formatted_time}")
                    await ctx.send(f"{magnitude}{magType} - {place} - {formatted_time}")
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


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        user_input = ctx.message.content.split()[0].replace("$", "")

        # list of available commands
        commands_list = [command.name for command in bot.commands]

        # find closest match
        suggestion = difflib.get_close_matches(user_input, commands_list, n = 1)

        if suggestion:
            await ctx.send(f"Command not found. Did you mean `${suggestion[0]}`?")
        else:
            await ctx.send("Command not found.")

    else:
        raise error


bot.run(token)
