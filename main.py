import sys

import discord
from dotenv import load_dotenv
import os

test_mode = True

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    new_activity = discord.Game(name="around in Python...")
    print(f"Logged in as {client.user}")
    await client.change_presence(activity=new_activity)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("[%s] Hello!" % os.getenv("environment_name"))
    elif message.content.startswith("$exit"):
        await message.channel.send("[%s] Ending connection..." % os.getenv("environment_name"))
        await client.close()

if __name__ == "__main__":

    load_dotenv()

    if os.getenv("mode") == "test":
        token = os.getenv("token_test")
    elif os.getenv("mode") == "prod":
        token = os.getenv("token_main")
    else:
        print("ERROR: No mode specified!")
        sys.exit(1)
    if token is None:
        print("ERROR: No token found!")
        sys.exit(1)

    client.run(token)
