import asyncio
import os

import smtplib
import ssl
import random
import threading
from datetime import datetime
from discord.ext import tasks
import time

import discord
import json

import cgh

port = 465
f = open("email_password.txt", "r")
password = f.read()
email = "noreply.iggybot@gmail.com"
message = """\
Subject: Verification Code

Hey there Crusader!\n
Your verification code for the Crusader Gaming Hub is: {code}\n
Please provide the code to Iggy, and you'll get access to the server. Thanks!\n\n

(This bot maintained by the Holy Cross Gaming & Esports Club.)"""

active_sessions = {}
# This is a dictionary
# {member:VerifySession}
# The below VerifySession class contains all the necessary data.

my_bot = None


class VerifySession:
    def __init__(self):
        self.code = ""
        self.email = ""
        self.channel = None
        self.menu_message = None
        self.classyear = 0
        self.group = ""  # can be current, former, guest, or prosp
        self.stage = 0


context = ssl.create_default_context()

if datetime.now().month < 6:
    year_senior = datetime.now().year
else:
    year_senior = datetime.now().year + 1

year_junior = year_senior + 1
year_sophomore = year_senior + 2
year_freshman = year_senior + 3
year_prospective = year_senior + 4


def get_embed_by_name(name, info):
    # Info is a dictionary in key:value form
    name = "embeds/" + name + ".json"
    if not os.path.isfile(name):
        return None
    with open(name) as jsonfile:
        data = json.load(jsonfile)

    if "fields" in data.keys() and info is not None:
        for field in data["fields"]:
            field["value"] = field["value"].format(**info)
    return discord.Embed.from_dict(data)


def send_code(user_email, code):
    # Actually sends the verification email.
    global message
    global email
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(email, password)
        local_message = message.format(code=code)
        server.sendmail(email, user_email, local_message)


def random_code(length):
    # Generates a random numerical code with provided length, and returns it as a string.
    code = ""
    for i in range(length):
        code += str(random.randint(0, 9))
    return code


def email_is_valid(supplied_email):
    # Checks if the given email is a Holy Cross email.
    # You will likely want to modify this.
    if supplied_email.endswith("@g.holycross.edu"):
        return True
    return False


async def session_cleanup(member):
    global active_sessions
    print("Channel deletion is scheduled.")
    await asyncio.sleep(30)
    print("Channel deletion is occurring.")
    await active_sessions[member].channel.delete(reason="Verification session ended.")
    print("Channel deleted.")
    del active_sessions[member]


async def guest_issue(member, approval):
    # Notifies user if their Guest Pass has been approved or denied.
    if approval is True:
        await active_sessions[member][4].edit(embed=get_embed_by_name("stage9_guest", "null"))
    else:
        await active_sessions[member][4].edit(embed=get_embed_by_name("stage4_denied", "null"))
    await session_cleanup(member)


async def alum_verify(member, approval):
    if approval is True:
        await active_sessions[member][4].edit(embed=get_embed_by_name("stage_7c_success", "null"))
    else:
        await active_sessions[member][4].edit(embed=get_embed_by_name("stage_7c_failure", "null"))
    await session_cleanup(member)


async def handle_interaction(interaction):
    # If this function has been called, we know the interaction is from a button and related to verification.
    # Therefore, we can assume it's valid.
    global active_sessions

    print("(verify.py - line 174)")
    print(interaction.data)
    member = interaction.user

    print(interaction.data["custom_id"])

    stage_data = interaction.data["custom_id"].replace("verify_", "")
    data_pieces = stage_data.split("_")

    # stage_data is always a string of form x_string to start, where x is the stage we are GOING TO
    # and string is the specific group flow we're in.
    # There may be additional data attached by underscore, depending on stage.

    stage = int(data_pieces[0])
    active_sessions[member].stage = stage
    active_sessions[member].group = data_pieces[1]

    resp_embed = get_embed_by_name("%s_%s" % (data_pieces[0], data_pieces[1]), "Null")

    if stage == 3 and active_sessions[member].classyear == 0:
        active_sessions[member].classyear = int(data_pieces[2])
        # If we're going to stage 3, then the user has just selected their class year.
        # We could also be entering stage 3 due to a re-enter request, in which case there's no year to parse.

    resp_view = discord.ui.View()

    if stage == 1:
        if active_sessions[member].group == "current":
            button_senior = discord.ui.Button(label=str(year_senior),
                                              custom_id="verify_3_current_%s" % str(year_senior),
                                              style=discord.ButtonStyle.blurple)
            button_junior = discord.ui.Button(label=str(year_junior),
                                              custom_id="verify_3_current_%s" % str(year_junior),
                                              style=discord.ButtonStyle.blurple)
            button_sophomore = discord.ui.Button(label=str(year_sophomore),
                                              custom_id="verify_3_current_%s" % str(year_sophomore),
                                              style=discord.ButtonStyle.blurple)
            button_freshman = discord.ui.Button(label=str(year_freshman),
                                              custom_id="verify_3_current_%s" % str(year_freshman),
                                              style=discord.ButtonStyle.blurple)

            resp_view.add_item(button_senior)
            resp_view.add_item(button_junior)
            resp_view.add_item(button_sophomore)
            resp_view.add_item(button_freshman)

        elif active_sessions[member].group == "former":

            for i in range(year_senior-1, year_senior-11, -1):
                print("Alumni looping!")
                temp_button = discord.ui.Button(label=str(i), custom_id="verify_3_former_%s" % str(i),
                                                style=discord.ButtonStyle.blurple)
                resp_view.add_item(temp_button)

            panic_button = discord.ui.Button(label="My year isn't listed!", custom_id="verify_2_former",
                                             style=discord.ButtonStyle.red)
            resp_view.add_item(panic_button)

        else:
            resp_view = None

    if resp_view is not None:
        resp_view.timeout = None
        for item in resp_view.children:
            item.callback = handle_interaction
    await interaction.response.edit_message(embed=resp_embed, view=resp_view)


async def new_input(member, u_input_str, origin_channel, raw_message):
    global active_sessions
    global my_bot
    if member not in active_sessions.keys():
        # Is the member actually getting verified?
        # If not, ignore it.
        return
    member_vs = active_sessions[member]  # The member is getting verified, pull their session.

    if origin_channel != member_vs.channel:
        # Was the message actually sent in their verification channel?
        # If not, ignore it.
        return

    resp_embed = discord.Embed()
    resp_view = discord.ui.View()
    resp_view.timeout = None
    if member_vs.group == "current":
        # The member is verifying as a current student.
        if member_vs.stage not in [3, 4]:
            # Is the member in a stage that actually expects text input?
            # If not, ignore their input.
            return

        if member_vs.stage == 3:
            # The user should have entered their email.
            if email_is_valid(u_input_str):
                # The email address is valid.
                member_vs.email = u_input_str
                member_vs.code = random_code(8)
                send_code(member_vs.email, member_vs.code)
                member_vs.stage = 4
                resp_embed = get_embed_by_name("4_current", {"email": member_vs.email})

                resend_button = discord.ui.Button(label="Resend Code", custom_id="verify_4_current",
                                                  style=discord.ButtonStyle.grey)
                resend_button.callback = handle_interaction

                reenter_button = discord.ui.Button(label="Re-enter Email", custom_id="verify_3_current",
                                                   style=discord.ButtonStyle.red)
                reenter_button.callback = handle_interaction

                resp_view.add_item(resend_button)
                resp_view.add_item(reenter_button)
                my_bot.add_view(resp_view)
            else:
                # Bad email address!
                resp_embed = get_embed_by_name("3_current_bademail", None)
        elif member_vs.stage == 4:
            # The user should have entered their verification code.
            if member_vs.code != u_input_str:
                # The code entered was invalid.
                resp_embed = get_embed_by_name("4_current_badcode", {"email": member_vs.email})
                resend_button = discord.ui.Button(label="Resend Code", custom_id="verify_4_current",
                                                  style=discord.ButtonStyle.grey)
                resend_button.callback = handle_interaction

                reenter_button = discord.ui.Button(label="Re-enter Email", custom_id="verify_3_current",
                                                   style=discord.ButtonStyle.red)
                reenter_button.callback = handle_interaction

                resp_view.add_item(resend_button)
                resp_view.add_item(reenter_button)
                my_bot.add_view(resp_view)
            else:
                # The code entered was valid! User verified!
                resp_embed = get_embed_by_name("6_current", None)
                resp_view = None
                asyncio.create_task(session_cleanup(member))

    elif member_vs.group == "former":
        # The member is verifying as a former student.
        if member_vs.stage not in [2, 3, 4]:
            # Is the member in a stage that actually expects text input?
            # If not, ignore their input.
            return
    else:
        # The member is verifying as a guest or accepted student, or does not have a group yet.
        if member_vs.stage != 1:
            # The process for guests and accepted students is much shorter because it involves manual oversight.
            # The only true stage in this flow is stage 1.
            # If we're somehow not in that stage....ignore it.
            return

    await member_vs.menu_message.edit(embed=resp_embed, view=resp_view)
    # Writes all updated data back to the master record.
    active_sessions[member] = member_vs


async def new_session(member):
    global active_sessions
    # Used to initiate a verification session over DMs with a user.
    # We call this function whenever someone new joins CGH.
    print("Starting new session...")
    verify_channel = await cgh.create_verify_session_channel(member)
    active_sessions[member] = VerifySession()

    group_view = discord.ui.View()
    group_button_current = discord.ui.Button(style=discord.ButtonStyle.grey, label="Current Student",
                                             custom_id="verify_1_current")
    group_button_former = discord.ui.Button(style=discord.ButtonStyle.grey, label="Former Student",
                                            custom_id="verify_1_former")
    group_button_guest = discord.ui.Button(style=discord.ButtonStyle.grey, label="Guest",
                                           custom_id="verify_1_guest")
    group_button_prosp = discord.ui.Button(style=discord.ButtonStyle.grey, label="Accepted/Prospective Student",
                                           custom_id="verify_1_prosp")

    group_view.add_item(group_button_current)
    group_view.add_item(group_button_former)
    group_view.add_item(group_button_guest)
    group_view.add_item(group_button_prosp)

    group_view.timeout = None

    for item in group_view.children:
        item.callback = handle_interaction

    my_bot.add_view(group_view)

    temp_message = await verify_channel.send(content=member.mention, embed=get_embed_by_name("0_all", None),
                                             view=group_view)

    active_sessions[member].channel = verify_channel
    active_sessions[member].menu_message = temp_message

