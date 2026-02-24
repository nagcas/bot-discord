import os
import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN_DISCORD")

URL_TERRAQUAKEAPI = "https://api.terraquakeapi.com/v1/earthquakes/recent"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)


@bot.command()
async def earthquake(ctx, arg):
    try:
        limit = arg.split(" ", 1)[0]
        response = requests.get(f"{URL_TERRAQUAKEAPI}?limit={limit}", timeout=10)

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
            await ctx.send(f"Latest {limit} seismic events:")
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
async def poke(ctx, arg):
    try:
        pokemon = arg.split(" ", 1)[0].lower()
        result = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon}/")
        if result.text == "Not Found":
            await ctx.send("Pokemon not found!")
        else:
            image_url = result.json()["sprites"]["front_default"]
            print(image_url)
            await ctx.send(image_url)

    except Exception as error:
        print("Error: ", error)


@poke.error
async def error_type(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("Send nombre Pokemon!")


@bot.command()
async def test(ctx, *args):
    response = " ".join(args)
    await ctx.send(response)


@bot.event
async def on_ready():
    print(f"Bot earthquake avviato! {bot.user}")


@bot.command()
async def clear(ctx):
    await ctx.channel.purge()
    await ctx.send("Messaggi cancellati!", delete_after=3)


bot.run(token)
