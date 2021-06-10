# VERSION 3.0 UPGRADE PROJECT
# STATUS: IN PROGRESS

from discord.ext import commands
from datetime import datetime
import discord
import verify
import cgh
import requests
import polls
import json as json
import os

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
    elif interaction.data["name"] == "embed":
        arg1 = interaction.data["options"][0]["value"]
        embed_to_print = verify.get_embed_by_name(arg1, "TestData")
        if embed_to_print is None:
            await interaction.followup.send("Embed not found!")
        else:
            await interaction.followup.send("Embed found! Printing...")
            await interaction.channel.send(embed=embed_to_print)
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
async def test(ctx, arg1):
    print("Heard test command!")
    if arg1 == "verify":
        await verify.new_session(ctx.author)
    elif arg1 == "react":
        await ctx.message.add_reaction("\U0001f7e9")
        await ctx.message.add_reaction("\U0001f7e5")
        await ctx.message.add_reaction('👍')
    elif arg1 == "welcome":
        await cgh.welcome_message(ctx.author)
    elif arg1 == "graduate":
        sen_count = await cgh.count_seniors(str(datetime.now().year))
        await ctx.send("Eligible Seniors: %d" % sen_count)
    elif arg1 == "emailparse":
        myembed = verify.get_embed_by_name("stage3", "ejfear21@g.holycross.edu")
        await ctx.send(embed=myembed)


@commands.command()
async def threadstart(ctx):
    global my_bot
    print("We are starting a thread!")
    await ctx.channel.set_permissions(my_bot.user, manage_threads=True, use_threads=True, use_private_threads=True)
    await ctx.channel.start_thread(name="Test Thread", message=ctx.message, auto_archive_duration=1440)


@commands.command()
async def stats(ctx):
    print("Heard stats command!")
    resp_embed = discord.Embed()
    resp_embed.colour = discord.Colour(3066993)
    resp_embed.title = "Current Server Statistics"
    resp_embed.add_field(name="Verified Members", value="%d" % cgh.count_members(), inline=True)
    resp_embed.add_field(name="Commands Used", value="%d" % -1, inline=True)

    await ctx.send(embed=resp_embed)


@commands.command(name="register")
async def role_reg(ctx, arg1, arg2):
    pass


@commands.command()
async def graduate(ctx):
    sen_count = await cgh.graduate_users(str(datetime.now().year))
    await ctx.send("Graduated Seniors: %d" % sen_count)


@commands.command()
async def embed(ctx, arg1):
    embed_to_print = verify.get_embed_by_name(arg1, "TestData")
    await ctx.send(embed=embed_to_print)


@commands.command()
async def csetup(ctx):
    # Runs registration of slash commands.
    f = open("token.txt", "r")
    bot_token = f.read()
    url = "https://discord.com/api/v9/applications/771800207733686284/guilds/432940415432261653/commands"
    headers = {
        "Authorization": "Bot %s" % bot_token
    }

    command_directory = "./commands"
    for file in os.listdir(command_directory):
        print(file)
        file = "commands/" + file
        with open(file) as jsonfile:
            data = json.load(jsonfile)
            r = requests.post(url, headers=headers, json=data)
            print("Received Status Code: %d" % r.status_code)


def setup(bot):
    global my_bot
    bot.add_command(csetup)
    bot.add_command(threadstart)
    my_bot = bot
    print("Setup completed successfully!")
    print(my_bot)




