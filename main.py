import os
import discord
from discord.ext import commands
import difflib
import requests
from datetime import datetime
from dotenv import load_dotenv
from earthquake_map import plotting

load_dotenv()
token = os.getenv("TOKEN_DISCORD")

URL_TERRAQUAKEAPI_RECENT = "https://api.terraquakeapi.com/v1/earthquakes/recent"
URL_TERRAQUAKEAPI_TODAY = "https://api.terraquakeapi.com/v1/earthquakes/today"
URL_TERRAQUAKEAPI_LAST_WEEK = "https://api.terraquakeapi.com/v1/earthquakes/last-week"
URL_TERRAQUAKEAPI_REGION = "https://api.terraquakeapi.com/v1/earthquakes/region"
URL_TERRAQUAKEAPI_EVENT = "https://api.terraquakeapi.com/v1/earthquakes/eventId"

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
        Returns the latest N earthquake events.
        Example: `$earthquake recent limit 5`
        
        ➡️ `$earthquake today limit <number>`
        This endpoint retrieves all seismic events that occurred today (from 00:00 UTC to the current time) from the TerraQuake API.
        Returns the latest N earthquakes recorded today.
        Example: `$earthquake today limit 10`
        
        ➡️ `$earthquake last-week limit <number>`
        This endpoint retrieves all seismic events that occurred in the last 7 days from the TerraQuake API.
        Returns the latest N earthquakes recorded last-week.
        Example: `$earthquake last-week limit 10`
        
        ➡️ `$earthquake region Calabria limit <number>`
        This endpoint retrieves all seismic events that occurred within a specific Italian region from the TerraQuake API, from the start of the current year up to today.
        Returns the latest N earthquakes recorded region.
        Example: `$earthquake region Calabria limit 10`
        
        ➡️ `$earthquake eventId <number id>`
        This endpoint retrieves a specific seismic event by its unique event ID from the TerraQuake API.
        Returns information about a specific earthquake event by event ID.
        Example: `$earthquake eventId 46060662`

        ➡️ `$test <text>`
        Repeats the input message
        Example: `$test hello`

        ➡️ `$info`
        Displays this guide

        ⚙️ **Data source:**
        TerraQuake API (real-time seismic events) - https://terraquakeapi.com -
        by Gianluca Chiaravalloti

        """
    await ctx.send(message)


@bot.command()
async def earthquake(ctx, *args):
    try:
        if len(args) < 1:
            await ctx.send("Usage: $earthquake (recent/today/last-week/region/eventId)")
            return

        mode = args[0]
        
        # Event id
        if mode == "eventId":
            
            if len(args) < 2:
                await ctx.send("Usage: $earthquake eventId <number id>")
                return
        
            event_id = args[1]
        
            url = f"{URL_TERRAQUAKEAPI_EVENT}?eventId={event_id}"
        
            await ctx.send(f"Searching seismic event ID {event_id}...")
        
        # Region        
        elif mode == "region":
            
            if len(args) > 4:
                await ctx.send("Usage: $eathquake region Calabria limit 10")
                return
            
            keyword = args[1]
            limit = int(args[3])
            url = f"{URL_TERRAQUAKEAPI_REGION}?region={keyword}&limit={limit}"
            await ctx.send(f"{mode} {keyword} seismic events:")
                
        # Recent/Today/Last-week  
        else:
            keyword = args[1]
            limit = int(args[2])
            
            if keyword != "limit":
                await ctx.send("Usage: $earthquake (recent or today or last-week or region) limit 10")
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
                await ctx.send("Invalid mode. Use recent or today or last-week or region.")
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
                    event_id = props.get("eventId", "N/A")
                    magnitude = props.get("mag", "N/A")
                    magType = props.get("magType", "Unknown")
                    place = props.get("place", "Unknown")
                    time = props.get("time")
                    
                    if time:
                        dt = datetime.fromisoformat(time)
                        formatted_time = dt.strftime("%d/%m/%Y %H:%M")
                    else:
                        formatted_time = "N/A"
                    
                    # EXTRA INFO FOR EVENTID
                    if mode == "eventId":
                        geometry = event.get("geometry", {})
                        coordinates = geometry.get("coordinates", [])
                        
                        if len(coordinates) >= 3:
                            lon = coordinates[0]
                            lat = coordinates[1]
                            depth = coordinates[2]
                        else:
                            lon = "N/A"
                            lat = "N/A"
                            depth = "N/A"

                        message = (
                            f"🌍 Event ID: {event_id}\n"
                            f"📍 Place: {place}\n"
                            f"📏 Magnitude: {magnitude}{magType}\n"
                            f"📌 Depth: {depth} km\n"
                            f"🧭 Coordinates: lat -> {lat}, lon -> {lon}\n"
                            f"🕒 Time: {formatted_time}"
                        )

                    else:

                        message = (
                            f"Event id: {event_id} - "
                            f"{magnitude}{magType} - "
                            f"{place} - "
                            f"{formatted_time}"
                        )

                    await ctx.send(message)

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

@bot.command()
async def plot(ctx):
    await ctx.send("Plot map")
    await plotting()


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
