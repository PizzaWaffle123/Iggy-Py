# VERSION 3.0 UPGRADE PROJECT
# STATUS: COMPLETE (Ready For 3.0)

import discord
import csv
import verify
import welcome

guild = None
roles = {}
channels = {}
requests = {}
my_bot = None


def setup(myguild, bot):
    global guild
    global roles
    global channels
    global my_bot
    guild = myguild
    with open('csv/roles.csv') as csvfile:
        rolereader = csv.reader(csvfile, dialect='excel')
        for role in rolereader:
            # each row of the csv file is in KEY,ROLE_ID format
            roles[role[0]] = int(role[1])
            print("Registered new role {} of ID {}".format(role[0], role[1]))

    with open('csv/channels.csv') as csvfile:
        channelreader = csv.reader(csvfile, dialect='excel')
        for channel in channelreader:
            channels[channel[0]] = int(channel[1])
            print("Registered new channel {} of ID {}".format(channel[0], channel[1]))

    my_bot = bot


def update_from_csv():
    global roles
    global channels
    with open('csv/roles.csv') as csvfile:
        rolereader = csv.reader(csvfile, dialect='excel')
        for role in rolereader:
            # each row of the csv file is in KEY,ROLE_ID format
            roles[role[0]] = int(role[1])
            print("Registered new role {} of ID {}".format(role[0], role[1]))

    with open('csv/channels.csv') as csvfile:
        channelreader = csv.reader(csvfile, dialect='excel')
        for channel in channelreader:
            channels[channel[0]] = int(channel[1])
            print("Registered new channel {} of ID {}".format(channel[0], channel[1]))


def get_channel_id_by_name(name):
    global channels
    if name in channels.keys():
        return channels[name]
    else:
        return None


def get_role_id_by_name(name):
    global roles
    if name in roles.keys():
        return roles[name]
    else:
        return None


def get_role_obj_by_name(name):
    global guild
    return guild.get_role(get_role_id_by_name(name))


def get_channel_obj_by_name(name):
    global guild
    return guild.get_channel(get_channel_id_by_name(name))


async def create_verify_session_channel(member):
    global guild
    category = get_channel_obj_by_name("cat_verify")
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        get_role_obj_by_name("eboard"): discord.PermissionOverwrite(read_messages=True),
        member: discord.PermissionOverwrite(read_messages=True)
    }
    channel_name = member.name + "-" + member.discriminator
    channel_name = channel_name.lower()

    channel = await guild.create_text_channel(channel_name, overwrites=overwrites, category=category)
    return channel


def count_members():
    # Returns a count of the members in the server who have specific roles.
    # In CGH, we use this to only count Crusaders and E-Board members. Guests and Pending users do not get counted.
    count = 0
    global roles
    global guild

    for member in guild.members:
        for role in member.roles:
            if role.id in [roles["crusader"], roles["eboard"]]:
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


async def verify_user(user, user_vs):
    member = guild.get_member(user_id=user.id)
    if member is None:
        return
    if guild.get_role(roles["pending"]) in member.roles:
        await member.remove_roles(guild.get_role(roles["pending"]))

    if user_vs.group in ["current", "former", "prosp"]:
        await member.add_roles(guild.get_role(roles["crusader"]))
        await member.add_roles(guild.get_role(roles[str(user_vs.classyear)]))

    if user_vs.group == "former":
        await member.add_roles(guild.get_role(roles["alumni"]))
    elif user_vs.group == "guest":
        await member.add_roles(guild.get_role(roles["guest"]))

    logged_user = verify.get_embed_by_name("user_log", user_vs.to_dict())
    logged_user.set_thumbnail(url=user.avatar_url)

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


async def welcome_message(member):
    global channels
    global guild
    await guild.get_channel(channels["server_work"]).send(content="<@&839897854712479784>",
                                                          embed=welcome.get_welcome_embed(member))


async def graduate_users(gradyear):
    global guild
    global roles
    grad_counter = 0
    year_role = guild.get_role(roles[gradyear])
    alum_role = guild.get_role(roles["alumni"])
    for member in guild.members:
        if year_role in member.roles:
            await member.add_roles(alum_role)
            grad_counter += 1
    print("Graduated %d users" % grad_counter)
    return grad_counter


async def count_seniors(gradyear):
    global guild
    global roles
    grad_counter = 0
    year_role = guild.get_role(roles[gradyear])
    for member in guild.members:
        if year_role in member.roles:
            grad_counter += 1
    print("Eligible seniors: %d" % grad_counter)
    return grad_counter


async def generate_verify_request(requester, requester_vs):
    # Parameters are the user requesting the pass and their VerifySession which includes all necessary data.
    global guild
    global channels
    global my_bot

    request_approval_buttons = discord.ui.View()
    request_btn_approve = discord.ui.Button(label="Approve", style=discord.ButtonStyle.green,
                                            custom_id="verify_6_%s_%s" % (requester_vs.group, str(requester.id)))
    request_btn_approve.callback = verify.handle_interaction

    request_btn_deny = discord.ui.Button(label="Deny", style=discord.ButtonStyle.red,
                                         custom_id="verify_7_%s_%s" % (requester_vs.group, str(requester.id)))
    request_btn_deny.callback = verify.handle_interaction

    request_approval_buttons.add_item(request_btn_approve)
    request_approval_buttons.add_item(request_btn_deny)

    request_embed = verify.get_embed_by_name("verify_request", requester_vs.to_dict())

    request_approval_buttons.timeout = None
    my_bot.add_view(request_approval_buttons)

    guild.get_channel(int(channels["member_log"])).send(embed=request_embed, view=request_approval_buttons)


async def user_left(member):
    # Used for logging users who leave the server.
    # Only logs departures of Crusaders and E-Board.
    valid = False
    global guild
    global roles

    for role in member.roles:
        if role.id in [roles["crusader"], roles["eboard"]]:
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
            bullhorn_embed = verify.get_embed_by_name("bullhorn")
            await bh_member.dm_channel.send(embed=bullhorn_embed)
            await bh_member.dm_channel.send(content=message.content)
        except discord.errors.Forbidden:
            print("UNABLE TO SEND BULLHORN - USER MAY HAVE DMs BLOCKED")









