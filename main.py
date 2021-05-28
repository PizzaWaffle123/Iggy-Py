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
    await cgh.get_channel_obj_by_name("server_work").send(embed=verify.get_embed_by_name("changelog", "TestData"))


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
    await verify.new_input(user, None, reaction, reaction.message.channel, reaction.message)
    if user == bot.user:
        return

    print("Checking to validate a guest pass or alum request...")
    if reaction.emoji == "\U0001f7e9":
        # Was it a green square?
        if reaction.message in cgh.guest_requests.keys():
            await cgh.verify_guest(reaction.message, True, user)
        elif reaction.message in cgh.alum_requests.keys():
            await cgh.verify_alum(reaction.message, True, user)
        else:
            return

    elif reaction.emoji == "\U0001f7e5":
        # How about a red square?
        if reaction.message in cgh.guest_requests.keys():
            await cgh.verify_guest(reaction.message, False, user)
        elif reaction.message in cgh.alum_requests.keys():
            await cgh.verify_alum(reaction.message, False, user)
        else:
            return

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

    # If the message was unrelated to verification, this will do nothing.
    await verify.new_input(message.author, message.content, None, message.channel, message)

    # If the message is a published webhook, bullhorn it!
    if message.channel.id == 840674330479689758 and message.webhook_id != 0:
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

