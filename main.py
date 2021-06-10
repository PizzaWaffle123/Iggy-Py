import discord
import cgh
import polls
import welcome
import verify
from discord.ext import commands
import commands as iggycommands

bot = commands.Bot(intents=discord.Intents.all(), command_prefix='$')


@bot.event
async def on_ready():
    # This event happens when the bot spins up.
    print('Logged on as {0}!'.format(bot.user))
    cgh.setup(bot.guilds[0])
    bot.load_extension('commands')
    verify.my_bot = bot
    await polls.refresh_from_file()
    # await cgh.get_channel_obj_by_name("server_work").send(embed=verify.get_embed_by_name("changelog", "TestData"))


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
async def on_interaction(interaction):
    print("Heard an interaction! (%s#%s)" % (interaction.user.name, interaction.user.discriminator))
    if "name" in interaction.data:
        print("I think it's a command!")
        await iggycommands.handle(interaction, bot)
    else:
        print("Could be a poll response!")
        await polls.handle_interaction(interaction)


@bot.event
async def on_message(message):
    # This event happens whenever the bot hears a message, either in a server or in a DM.
    if message.author == bot.user:
        return

    # If the message was unrelated to verification, this will do nothing.
    await verify.new_input(message.author, message.content, message.channel, message)

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

