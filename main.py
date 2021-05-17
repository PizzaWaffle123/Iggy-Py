import discord
import cgh
import welcome
import verify
from discord.ext import commands

bot = commands.Bot(intents=discord.Intents.all(), command_prefix='$')


@bot.event
async def on_ready():
    # This event happens when the bot spins up.
    print('Logged on as {0}!'.format(bot.user))
    cgh.setup(bot.guilds[0])
    bot.load_extension('commands')


@bot.event
async def on_member_join(member):
    # This event happens when someone joins a server the bot is part of.
    await cgh.new_user(member)
    await verify.new_session(member)


@bot.event
async def on_member_leave(member):
    # This event happens when someone leaves a server the bot is part of.
    await cgh.user_left(member)


@bot.event
async def on_user_update(before, after):
    # This event happens when something (username, nickname, pfp) about a server member changes.
    # In CGH, we use this to notify us of username changes only.
    before_name = "%s#%s" % (before.name, before.discriminator)
    after_name = "%s#%s" % (after.name, after.discriminator)
    if before_name != after_name:
        await cgh.username_update(before, after)


@bot.event
async def on_reaction_add(reaction, user):
    # This event happens whenever a reaction gets added to a message the bot can see.
    print("Heard a reaction added!")
    print(reaction.emoji)
    if reaction.message not in cgh.guest_requests.keys():
        await verify.new_input(user, None, reaction)
        return
    if user == bot.user:
        return

    if reaction.emoji == "\U0001f7e9":
        # Was it a green square?
        await cgh.verify_guest(reaction.message)
        relevant_user = cgh.guest_requests[reaction.message]
        await verify.guest_issue(relevant_user, True)
        del cgh.guest_requests[reaction.message]
        embed_to_edit = reaction.message.embeds[0]
        embed_to_edit.title = "Guest Pass Approved"
        embed_to_edit.description = ""
        embed_to_edit.add_field(name="Approved By", value="%s#%s" % (user.name, user.discriminator), inline=False)
        embed_to_edit.colour = discord.Colour(3066993)
        await reaction.message.edit(embed=embed_to_edit)

    elif reaction.emoji == "\U0001f7e5":
        # How about a red square?
        relevant_user = cgh.guest_requests[reaction.message]
        await verify.guest_issue(relevant_user, False)
        del cgh.guest_requests[reaction.message]
        embed_to_edit = reaction.message.embeds[0]
        embed_to_edit.title = "Guest Pass Denied"
        embed_to_edit.description = ""
        embed_to_edit.add_field(name="Denied By", value="%s#%s" % (user.name, user.discriminator), inline=False)
        embed_to_edit.colour = discord.Colour(15158332)
        await reaction.message.edit(embed=embed_to_edit)

    else:
        # We can ignore it
        return


@bot.event
async def on_member_update(before, after):
    # This event happens whenever something server-specific happens to a user.
    # We use this to track role changes.
    before_roles = set(before.roles)
    after_roles = set(after.roles)
    role_changed = after_roles - before_roles
    for role in role_changed:
        if role.id == cgh.get_role_id_by_name("crusader"):
            cgh.welcome_message(after)
            break


@bot.event
async def on_message(message):
    # This event happens whenever the bot hears a message, either in a server or in a DM.
    if message.author == bot.user:
        return

    # If the message is sent in a DM channel, do a verification thing.
    if isinstance(message.channel, discord.DMChannel):
        results = await verify.new_input(message.author, message.content, None)
        if results[0] == 2:
            await cgh.verify_user(message.author, results[1])
        elif results[0] == 3:
            await cgh.notify_of_guest(message.author)
        elif results[0] == 4:
            await cgh.verify_guest(message.author)

    # If the message is a published webhook, bullhorn it!
    elif message.channel.id == 840674330479689758 and message.webhook_id != 0:
        # We received a published announcement and confirmed it was a webhook!
        print("Heard a published announcement!")
        await cgh.bullhorn_send(message)

    # It's possibly a command?
    else:
        await bot.process_commands(message)


# Sets the status of the bot, visible in user sidebar.
bot.activity = discord.Activity(name="Version 3.0-TEST", type=discord.ActivityType.competing)
# Starts the bot.
f = open("token.txt", "r")
bot_token = f.read()

bot.run(bot_token)

