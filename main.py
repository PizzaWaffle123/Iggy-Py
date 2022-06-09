import sys

import discord
from dotenv import load_dotenv
import os

import commands
import database
import directory

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

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
    ct.add_command(commands.co_test, guild=client.guilds[0])
    ct.add_command(commands.co_sql, guild=client.guilds[0])
    ct.add_command(commands.co_welcome, guild=client.guilds[0])
    ct.add_command(commands.co_modal, guild=client.guilds[0])
    ct.add_command(commands.co_dbupdate, guild=client.guilds[0])

    # Step 2 - User context actions.
    ct.add_command(commands.ca_user_identify, guild=client.guilds[0])

    # Step 3 - Message context actions.
    ct.add_command(commands.ca_message_thumbs, guild=client.guilds[0])

    # Step 4 - Synchronize.
    await ct.sync(guild=client.guilds[0])
    count_slash = len(ct.get_commands(guild=client.guilds[0], type=discord.AppCommandType.chat_input))
    count_ca_user = len(ct.get_commands(guild=client.guilds[0], type=discord.AppCommandType.user))
    count_ca_message = len(ct.get_commands(guild=client.guilds[0], type=discord.AppCommandType.message))

    print(f"Synchronized {count_slash} slash commands.")
    print(f"Synchronized {count_ca_user} user context actions.")
    print(f"Synchronized {count_ca_message} message context actions.")


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
