import sys

import discord
from dotenv import load_dotenv
import os

import commands
import database
import directory
import welcome

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
ct = None


@client.event
async def on_ready():
    global ct
    new_activity = discord.Game(name="around in Python...")
    print(f"Logged in as {client.user}")
    await client.change_presence(activity=new_activity)

    # Synchronizes commands and binds them to local handlers.
    ct = discord.app_commands.CommandTree(client)
    await ct.fetch_commands(guild=client.guilds[0])
    # Step 1 - Slash commands.
    ct.add_command(commands.test, guild=client.guilds[0])
    ct.add_command(commands.sql, guild=client.guilds[0])
    ct.add_command(commands.welcome, guild=client.guilds[0])
    ct.add_command(commands.modal, guild=client.guilds[0])

    # Step 2 - Context actions.
    ct.add_command(commands.ca_identify, guild=client.guilds[0])
    await ct.sync(guild=client.guilds[0])


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("[%s] Hello!" % os.getenv("environment_name"))
    elif message.content.startswith("$exit"):
        await message.channel.send("[%s] Ending connection..." % os.getenv("environment_name"))
        await client.close()
    elif message.content.startswith("$sql"):
        pieces = message.content.split(" ", 1)
        data = database.raw_query(pieces[1])
        await message.channel.send(data)
    elif message.content.startswith("$whois"):
        pieces = message.content.split(" ", 1)
        data = directory.get_user(pieces[1])
        await message.channel.send(data)


if __name__ == "__main__":

    load_dotenv()

    token = os.getenv("token")

    if token is None:
        print("ERROR: No token found!")
        sys.exit(1)

    client.run(token)
