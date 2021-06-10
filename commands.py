import time

from discord.ext import commands
from datetime import datetime
import discord
import verify
import cgh
import requests
import polls
import json as json
import os

import welcome

my_bot = None


async def handle(interaction, bot):
    global my_bot
    my_bot = bot

    print(interaction.data)
    await interaction.response.defer(ephemeral=True)

    if interaction.data["name"] == "test":
        if interaction.data["options"][0]["value"] == "verify":
            await verify.new_session(interaction.user)
            await interaction.followup.send(content="Test command used!")
        elif interaction.data["options"][0]["value"] == "welcome":
            resp_embed = welcome.get_welcome_embed(interaction.user)
            await interaction.followup.send(embed=resp_embed)
        elif interaction.data["options"][0]["value"] == "graduate":
            sen_count = await cgh.count_seniors(str(datetime.now().year))
            await interaction.followup.send("Eligible Seniors: %d" % sen_count)
    elif interaction.data["name"] == "embed":
        arg1 = interaction.data["options"][0]["value"]
        embed_to_print = verify.get_embed_by_name(arg1, "TestData")
        if embed_to_print is None:
            await interaction.followup.send("Embed not found!")
        else:
            await interaction.followup.send("Embed found! Printing...")
            await interaction.channel.send(embed=embed_to_print)
    elif interaction.data["name"] == "changelog":
        embed_to_print = verify.get_embed_by_name("changelog", None)
        await interaction.followup.send(embed=embed_to_print)
    elif interaction.data["name"] == "poll":
        interaction_info = interaction.data["options"][0]
        if interaction_info["name"] == "create":
            prompt = interaction_info["options"][0]["value"]
            options = interaction_info["options"][1]["value"].split("|")

            poll_view = discord.ui.View()
            for opt in options:
                poll_view.add_item(discord.ui.Button(label=opt, style=discord.ButtonStyle.blurple, custom_id=opt))
            for item in poll_view.children:
                item.callback = polls.handle_interaction

            poll_view.timeout = None
            my_bot.add_view(poll_view)

            poll_message = await interaction.channel.send(content="Generating poll...", view=poll_view)

            await polls.track_new_poll(poll_message, options, prompt)
            await interaction.followup.send(content="Poll created!")
        elif interaction_info["name"] == "end":
            poll_to_end = interaction_info["options"][0]["value"]
            if await polls.end_poll(poll_to_end) is True:
                await interaction.followup.send(content="Poll ended!")
            else:
                await interaction.followup.send(content="Unable to end poll - did you type the ID correctly?")
    elif interaction.data["name"] == "count":
        resp_embed = discord.Embed()
        resp_embed.title = "SERVER COUNT"
        resp_embed.description = "%d" % cgh.count_members()
        resp_embed.colour = discord.Colour(4171755)
        await interaction.followup.send(embed=resp_embed)
    elif interaction.data["name"] == "graduate":
        sen_count = await cgh.graduate_users(str(datetime.now().year))
        await interaction.followup.send("Graduated Seniors: %d" % sen_count)


@commands.command()
async def csetup(ctx):
    # Runs registration of slash commands.
    await ctx.send(content="Attemtping to register slash commands...")
    f = open("token.txt", "r")
    bot_token = f.read()
    url = "https://discord.com/api/v9/applications/771800207733686284/guilds/432940415432261653/commands"
    headers = {
        "Authorization": "Bot %s" % bot_token
    }

    command_directory = "./commands"
    command_queue = []
    for file in os.listdir(command_directory):
        print(file)
        file = "commands/" + file
        command_queue.append(file)

    while command_queue:
        print("Current Command Queue:")
        print(command_queue)
        rate_limit_time = 4
        for file in command_queue:
            with open(file) as jsonfile:
                data = json.load(jsonfile)
                r = requests.post(url, headers=headers, json=data)
                print("Received Status Code: %d" % r.status_code)
                if r.status_code in [200, 201]:
                    command_queue.remove(file)
                    print("Added command successfully!")
                    await ctx.send(content="Added command: %s" % file)
                if r.status_code == 429:
                    # We are being rate limited.
                    rate_limit_dict = json.loads(r.content)
                    print(r.content)
                    rate_limit_time = float(rate_limit_dict["retry_after"])
        time.sleep(int(rate_limit_time) + 1)

    await ctx.send(content="Added all commands!")

    with open("./config/permissions.json") as permfile:
        data = json.load(permfile)
        r = requests.put(url + "/permissions", headers=headers, json=data)
        print("[PERMS] Received Status Code: %d" % r.status_code)
        print(r.content)


def setup(bot):
    global my_bot
    bot.add_command(csetup)
    my_bot = bot
    print("Setup completed successfully!")
    print(my_bot)




