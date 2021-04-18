import discord
import cgh
import welcome
import verify

client = discord.Client(intents=discord.Intents.all())
my_cgh = None


@client.event
async def on_ready():
    # This event happens when the bot spins up.
    global my_cgh
    print('Logged on as {0}!'.format(client.user))
    my_cgh = cgh.CGH(client.guilds[0])


@client.event
async def on_member_join(member):
    # This event happens when someone joins a server the bot is part of.
    global my_cgh
    await my_cgh.new_user(member)
    await verify.new_session(member)


@client.event
async def on_member_leave(member):
    # This event happens when someone leaves a server the bot is part of.
    global my_cgh
    await my_cgh.user_left(member)


@client.event
async def on_user_update(before, after):
    # This event happens when something (username, nickname, pfp) about a server member changes.
    # In CGH, we use this to notify us of username changes only.
    before_name = "%s#%s" % (before.name, before.discriminator)
    after_name = "%s#%s" % (after.name, after.discriminator)
    if before_name != after_name:
        await my_cgh.username_update(before, after)


@client.event
async def on_reaction_add(reaction, user):
    # This event happens whenever a reaction gets added to a message the bot can see.
    print("Heard a reaction added!")
    print(reaction.emoji)
    if reaction.message not in my_cgh.guest_requests.keys():
        return
    if user == client.user:
        return

    if reaction.emoji == "\U0001f7e9":
        # Was it a green square?
        await my_cgh.verify_guest(reaction.message)
        relevant_user = my_cgh.guest_requests[reaction.message]
        await verify.guest_issue(relevant_user, True)
        del my_cgh.guest_requests[reaction.message]
        embed_to_edit = reaction.message.embeds[0]
        embed_to_edit.title = "Guest Pass Approved"
        embed_to_edit.description = ""
        embed_to_edit.add_field(name="Approved By", value="%s#%s" % (user.name, user.discriminator), inline=False)
        embed_to_edit.colour = discord.Colour.from_rgb(126, 211, 33)
        await reaction.message.edit(embed=embed_to_edit)

    elif reaction.emoji == "\U0001f7e5":
        # How about a red square?
        relevant_user = my_cgh.guest_requests[reaction.message]
        await verify.guest_issue(relevant_user, False)
        del my_cgh.guest_requests[reaction.message]
        embed_to_edit = reaction.message.embeds[0]
        embed_to_edit.title = "Guest Pass Denied"
        embed_to_edit.description = ""
        embed_to_edit.add_field(name="Denied By", value="%s#%s" % (user.name, user.discriminator), inline=False)
        embed_to_edit.colour = discord.Colour.from_rgb(214, 40, 61)
        await reaction.message.edit(embed=embed_to_edit)

    else:
        # We can ignore it
        return


@client.event
async def on_member_update(before, after):
    # This event happens whenever something server-specific happens to a user.
    # We use this to track role changes.
    before_roles = set(before.roles)
    after_roles = set(after.roles)
    role_changed = after_roles - before_roles
    if my_cgh.role_crusader in role_changed:
        print("The Crusader role was appended to somebody!")
        await my_cgh.channel_general.send(embed=welcome.get_welcome_embed(after, my_cgh.count_members()))


@client.event
async def on_message(message):
    # This event happens whenever the bot hears a message, either in a server or in a DM.
    if message.author == client.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        results = await verify.new_dm_input(message.author, message.content)
        if results[0] == 2:
            await my_cgh.verify_user(message.author, results[1])
        elif results[0] == 3:
            await my_cgh.notify_of_guest(message.author)
        elif results[0] == 4:
            await my_cgh.verify_guest(message.author)

    elif not message.content.startswith("$"):
        return

    if message.content.startswith("$count"):
        await message.channel.send("%d" % my_cgh.count_members())

    elif message.content.startswith("$test"):
        message_parts = message.content.split(" ")
        if len(message_parts) < 2:
            return
        if message_parts[1] == "verify":
            await verify.new_session(message.author)
        if message_parts[1] == "react":
            await message.add_reaction("\U0001f7e9")
            await message.add_reaction("\U0001f7e5")
            await message.add_reaction('👍')


# Sets the status of the bot, visible in user sidebar.
client.activity = discord.Activity(name="in TEST MODE", type=discord.ActivityType.playing)
# Starts the bot.
client.run("PUT YOUR DISCORD BOT TOKEN INSIDE THESE QUOTES")
