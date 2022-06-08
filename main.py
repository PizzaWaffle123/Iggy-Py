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


@client.event
async def on_interaction(interaction):
    # Oh god oh fuck.
    print("Heard an interaction!")
    match interaction.type:
        case discord.InteractionType.modal_submit:
            # A modal was submitted.
            print("Modal submission!")
        case discord.InteractionType.application_command:
            print("Application command!")
            """
            Within interaction.data is a type value of an integer. These values are:
            1 - Slash Command.
            2 - Context Action on User
            3 - Context Action on Message
            """
            match interaction.data["type"]:
                case 1:
                    print("Slash command!")
                    match interaction.data["name"]:
                        case "welcome":
                            await interaction.response.send_message(
                                embeds=[welcome.get_welcome_embed(interaction.user, "Test introduction!")]
                            )
                        case "sql":
                            query = interaction.data["options"][0]["value"]
                            await interaction.response.send_message(database.raw_query(query))
                case 2:
                    print("Context action - user!")
                    match interaction.data["name"].lower():
                        case "identify":
                            user_id = interaction.data["target_id"]
                            user_data = database.identify_user(user_id)
                            """
                                user_data now contains a 5-tuple with the following values:
                                - User ID
                                - User full name
                                - User grad year
                                - User email stub
                                - Username#Discriminator
                            """
                            datastring = f"Name: {user_data[1]}\n" \
                                         f"Graduation Year: {user_data[2]}\n" \
                                         f"Email: {user_data[3]}@g.holycross.edu"
                            await interaction.response.send_message(
                                ephemeral=True,
                                content=datastring
                            )
                case 3:
                    print("Context action - message!")


if __name__ == "__main__":

    load_dotenv()

    token = os.getenv("token")

    if token is None:
        print("ERROR: No token found!")
        sys.exit(1)

    client.run(token)
