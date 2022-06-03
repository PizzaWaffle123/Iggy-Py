import sys

import discord
from dotenv import load_dotenv
import os

import database
import directory
import welcome

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
    if message.content.startswith("$help"):
        help_embed = discord.Embed(title="Commands", description="", color=0xb26aff)
        help_embed.add_field(name="help",
                             value="List all available commands.",
                             inline=False)
        help_embed.add_field(name="hello",
                             value="Dev says hello!",
                             inline=False)
        help_embed.add_field(name="exit",
                             value="Dev ends all connections.",
                             inline=False)
        help_embed.add_field(name="sql",
                             value="User can enter SQL code to retrieve data.",
                             inline=False)
        help_embed.add_field(name="whois",
                             value="Retrieve information about a user.",
                             inline=False)
        await message.channel.send(embed=help_embed)
    elif message.content.startswith("$hello"):
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


@client.event
async def on_interaction(interaction):
    # Oh god oh fuck.
    print("Heard an interaction!")
    match interaction.type:
        case discord.InteractionType.modal_submit:
            # A modal was submitted.
            print("Modal submission!")
        case discord.InteractionType.application_command:
            # A command or context action was used.
            match interaction.data["name"]:
                case "welcome":
                    await interaction.response.send_message(embeds=[welcome.get_welcome_embed(interaction.user)])
                case "sql":
                    query = interaction.data["options"][0]["value"]
                    await interaction.response.send_message(database.raw_query(query))


if __name__ == "__main__":

    load_dotenv()

    token = os.getenv("token")

    if token is None:
        print("ERROR: No token found!")
        sys.exit(1)

    client.run(token)
