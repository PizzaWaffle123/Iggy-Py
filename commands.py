# VERSION 3.0 UPGRADE PROJECT
# STATUS: IN PROGRESS

from discord.ext import commands
from datetime import datetime
import discord
import verify
import cgh

command_counter = 0


@commands.command()
async def test(ctx, arg1):
    global command_counter
    command_counter += 1
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


@commands.command()
async def count(ctx):
    global command_counter
    command_counter += 1
    print("Heard count command!")
    resp_embed = discord.Embed()
    resp_embed.title = "SERVER COUNT"
    resp_embed.description = "%d" % cgh.count_members()
    resp_embed.color = discord.Colour(4171755)

    await ctx.send(embed=resp_embed)


@commands.command()
async def stats(ctx):
    global command_counter
    command_counter += 1
    print("Heard stats command!")
    resp_embed = discord.Embed()
    resp_embed.color = discord.Colour(3066993)
    resp_embed.title = "Current Server Statistics"
    resp_embed.add_field(name="Verified Members", value="%d" % cgh.count_members(), inline=True)
    resp_embed.add_field(name="Commands Used", value="%d" % command_counter, inline=True)

    await ctx.send(embed=resp_embed)


@commands.command(name="register")
async def role_reg(ctx, arg1, arg2):
    pass


@commands.command()
async def graduate(ctx):
    sen_count = await cgh.graduate_users(str(datetime.now().year))
    await ctx.send("Graduated Seniors: %d" % sen_count)


def setup(bot):
    bot.add_command(test)
    bot.add_command(count)
    bot.add_command(stats)
    bot.add_command(graduate)
