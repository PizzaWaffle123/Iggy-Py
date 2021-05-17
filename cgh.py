# VERSION 3.0 UPGRADE PROJECT
# STATUS: COMPLETE (Ready For 3.0)

import discord
import csv

guild = None
roles = {}
channels = {}
guest_requests = {}


def setup(myguild):
    global guild
    global roles
    global channels
    guild = myguild
    with open('csv/roles.csv') as csvfile:
        rolereader = csv.reader(csvfile, dialect='excel')
        for role in rolereader:
            # each row of the csv file is in KEY,ROLE_ID format
            roles[role[0]] = role[1]
            print("Registered new role {} of ID {}".format(role[0], role[1]))

    with open('csv/channels.csv') as csvfile:
        channelreader = csv.reader(csvfile, dialect='excel')
        for channel in channelreader:
            channels[channel[0]] = channel[1]
            print("Registered new channel {} of ID {}".format(channel[0], channel[1]))


def count_members():
    # Returns a count of the members in the server who have specific roles.
    # In CGH, we use this to only count Crusaders and E-Board members. Guests and Pending users do not get counted.
    count = 0
    global roles
    global guild

    for member in guild.members:
        for role in member.roles:
            if str(role.id) in [roles["crusader"], roles["eboard"]]:
                count += 1
                break
    return count


async def new_user(user):
    global roles
    global guild
    # Simply adds the Pending role to the user provided as a parameter.
    member = guild.get_member(user_id=user.id)
    if member is None:
        return
    role_pending = guild.get_role(roles["pending"])
    await member.add_roles(role_pending)


async def verify_user(user, user_email, gradyear):
    global roles
    global guild
    global channels
    # This function gets called when a user has completed verification.
    # It is used for role adjustment and logging.
    member = guild.get_member(user_id=user.id)
    if member is None:
        return

    if guild.get_role(roles["pending"]) in member.roles:
        await member.remove_roles(guild.get_role(roles["pending"]))
    await member.add_roles(guild.get_role(roles["crusader"]))
    await member.add_roles(guild.get_role(roles[gradyear]))
    logged_user = discord.Embed()
    logged_user.title = "New Verified User"
    logged_user.add_field(name="Username", value="%s#%s" % (user.name, user.discriminator), inline=False)
    logged_user.add_field(name="Email Address", value=user_email, inline=False)
    logged_user.add_field(name="Year of Graduation", value=gradyear, inline=False)
    logged_user.set_thumbnail(url=user.avatar_url)
    logged_user.colour = discord.Colour(3066993)
    await guild.get_channel(channels["member_log"]).send(embed=logged_user)


async def username_update(u_before, u_after):
    # Handles logging of users changing their username.
    old_username = "%s#%s" % (u_before.name, u_before.discriminator)
    new_username = "%s#%s" % (u_after.name, u_after.discriminator)
    username_change = discord.Embed()
    username_change.title = "User Changed Name"
    username_change.colour = discord.Colour(16295218)
    username_change.description = "Don't forget to update the Discord roster!"
    username_change.add_field(name="Previous", value=old_username, inline=True)
    username_change.add_field(name="Current", value=new_username, inline=True)
    await guild.get_channel(channels["member_log"]).send(embed=username_change)


async def notify_of_guest(user):
    global guild
    global guest_requests

    # Creates dynamic Guest Pass embed usable by moderators.
    guest_request = discord.Embed()
    guest_request.title = "Guest Pass Requested"
    guest_request.set_thumbnail(url=user.avatar_url)
    guest_request.description = "\U0001f7e9 Approve\n" \
                                "\U0001f7e5 Deny"
    guest_request.add_field(name="Username", value="%s#%s" % (user.name, user.discriminator), inline=False)
    guest_request.colour = discord.Colour.from_rgb(12042958)
    sent_message = await guild.get_channel(channels["member_log"]).send(embed=guest_request)
    await sent_message.add_reaction("\U0001f7e9")  # green square
    await sent_message.add_reaction("\U0001f7e5")  # red square
    guest_requests[sent_message] = user


async def verify_guest(message):
    # Used to "approve" a Guest Pass.
    global guild
    global roles
    global guest_requests

    if message not in guest_requests.keys():
        return
    user = guest_requests[message]
    member = guild.get_member(user_id=user.id)
    if member is None:
        return
    if guild.get_role(roles["pending"]) in member.roles:
        await member.remove_roles(guild.get_role(roles["pending"]))
    await member.add_roles(guild.get_role(roles["guest"]))


async def user_left(member):
    # Used for logging users who leave the server.
    # Only logs departures of Crusaders and E-Board.
    valid = False
    global guild
    global roles

    for role in member.roles:
        if str(role.id) in [roles["crusader"], roles["eboard"]]:
            valid = True
            break

    if valid is False:
        return

    departure_notice = discord.Embed()
    departure_notice.title = "User Left Server"
    departure_notice.add_field(name="Remaining Members", value="➤ %d" % count_members(), inline=False)
    departure_notice.colour = discord.Colour(15158332)
    departure_notice.set_author(name="%s#%s" % (member.name, member.discriminator), url=None,
                                icon_url=member.avatar_url)
    await guild.get_channel(channels["member_log"]).send(embed=departure_notice)


async def bullhorn_send(message):
    global guild
    global roles

    bullhorn_list = []
    for member in guild.members:
        # Step 1: Identify all users opted in to Bullhorn.
        bullhorn_mem = False
        for role in member.roles:
            if str(id) == roles["bullhorn"]:
                bullhorn_mem = True
                break
        if bullhorn_mem:
            bullhorn_list.append(member)

    for bh_member in bullhorn_list:
        # Step 2: Send the message to all users opted in to Bullhorn.
        if bh_member.dm_channel is None:
            await bh_member.create_dm()
        try:
            print("Sending bullhorn to user: " + bh_member.name)
            await bh_member.dm_channel.send("Incoming Bullhorn from the Crusader Gaming Hub!")
            await bh_member.dm_channel.send(content=message.content)
        except discord.errors.Forbidden:
            print("UNABLE TO SEND BULLHORN - USER MAY HAVE DMs BLOCKED")









