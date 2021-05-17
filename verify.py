import csv
import smtplib
import ssl
import random
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

active_sessions = {}  # dictionary in format member:(stage,code,email,classyear,menu_message,channel)
# stage is int, menu_message is message, channel is channel, all others are string
# Quick reminder of verification stages
# Stage 0 - User has just joined CGH.
# User is prompted to react on the menu to declare what group they are in (Student, Guest, etc.)
# Available groups are: Student, Prospective, Guest, Alumnus/Alumna
# Stage 1 - User has selected Student and must now select their class year.
# Stage 2 - User has selected their class year and we are now waiting for them to provide their email address.
# Stage 3 - User has provided a valid email address, and we are now waiting for them to provide the security code.
# User may also opt to re-send verification code if they have not received one.
# User may also opt to return to Stage 2 and re-enter their email.
# Stage 4 - User has selected Guest and is now waiting for an approval/denial.
# Stage 5 - User has selected Prospective and must now enter their full name to continue.
# Stage 6 - User has selected Alumnus/Alumna and must now select their year of graduation.
# Stage 7 - User has selected their class year and we are now waiting for them to provide their email address.
# User may also react here to indicate they do not have access to their Holy Cross email address.
# This will prompt moderators to perform a manual verification.
# Stage 8 - User provided a valid email address and we are now waiting for them to provide the security code.
# See notes for stage 3.
# Stage 9 - This is the "success" generic stage. It occurs in the following cases:
# STUDENT - User verified a valid student email address.
# ALUM - User verified a valid email address OR otherwise proved they are an alum.
# GUEST - User's guest pass request was approved.
# PROSPECTIVE - User entered their full name.

context = ssl.create_default_context()


def get_embed_by_name(name):
    name = "embeds/" + name + ".json"
    with open(name) as jsonfile:
        data = json.load(jsonfile)
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
    print("Channel deletion in 30 seconds.")
    await active_sessions[member][5].send(content=member.mention + "\nYour verification session has concluded. This "
                                                                   "channel will automatically delete in 30 seconds.")
    time.sleep(30)
    await active_sessions[member][5].delete(reason="Verification session ended.")
    print("Channel deleted.")
    del active_sessions[member]


async def guest_issue(member, approval):
    # Notifies user if their Guest Pass has been approved or denied.
    if approval is True:
        await active_sessions[member][4].edit(embed=get_embed_by_name("stage9_guest"))
    else:
        await active_sessions[member][4].edit(embed=get_embed_by_name("stage4_denied"))
    await session_cleanup(member)


async def new_input(member, u_input_str, u_input_react):
    global active_sessions
    # Returns a Tuple (user stage, response info)
    # This function happens whenever a user reacts or says something in the DM channel.
    # u_input_str is whatever the user typed, u_input_react is the Reaction event if applicable.
    # either of these values can be None, but one must always be non-None.
    if member not in active_sessions.keys():
        return
    member_vs = active_sessions[member]  # vs stands for "verify state", see above
    if u_input_react is None and u_input_str is None:
        # We should...never be here. Time to panic.
        return

    if member_vs[0] == 0:
        # We are expecting a reaction.
        if u_input_react.emoji == "🟣":
            # Purple Circle - STUDENT
            print("Student!")
            active_sessions[member] = (1, member_vs[1], member_vs[2], member_vs[3], member_vs[4], member_vs[5])
            await active_sessions[member][4].edit(embed=get_embed_by_name("stage1"))
            await member_vs[4].clear_reactions()

            await member_vs[4].add_reaction("🇦")
            await member_vs[4].add_reaction("🇧")
            await member_vs[4].add_reaction("🇨")
            await member_vs[4].add_reaction("🇩")
        elif u_input_react.emoji == "⚪":
            # White Circle - GUEST
            print("Guest!")
            active_sessions[member] = (4, member_vs[1], member_vs[2], member_vs[3], member_vs[4], member_vs[5])
            await active_sessions[member][4].edit(embed=get_embed_by_name("stage4"))
            await member_vs[4].clear_reactions()
            await cgh.notify_of_guest(member)
        elif u_input_react.emoji == "🟡":
            # Yellow Circle - PROSPECTIVE
            print("Prospective!")
            active_sessions[member] = (5, member_vs[1], member_vs[2], member_vs[3], member_vs[4], member_vs[5])
            await active_sessions[member][4].edit(embed=get_embed_by_name("stage5"))
            await member_vs[4].clear_reactions()
        elif u_input_react.emoji == "🔵":
            # Blue Circle - ALUM
            print("Alum!")
            active_sessions[member] = (6, member_vs[1], member_vs[2], member_vs[3], member_vs[4], member_vs[5])
            await active_sessions[member][4].edit(embed=get_embed_by_name("stage6"))
            await member_vs[4].clear_reactions()
        else:
            return
    elif member_vs[0] == 1:
        # User has picked their class year.
        if u_input_react.emoji == "🇦":
            pass
        elif u_input_react.emoji == "🇧":
            pass
        elif u_input_react.emoji == "🇨":
            pass
        elif u_input_react.emoji == "🇩":
            pass
        else:
            return
        await session_cleanup(member)


async def new_session(member):
    global active_sessions
    # Used to initiate a verification session over DMs with a user.
    # We call this function whenever someone new joins CGH.
    print("Starting new session...")
    verify_channel = await cgh.create_verify_session_channel(member)
    temp_message = await verify_channel.send(content=member.mention, embed=get_embed_by_name("stage0"))

    await temp_message.add_reaction("🟣")
    await temp_message.add_reaction("⚪")
    await temp_message.add_reaction("🟡")
    await temp_message.add_reaction("🔵")
    active_sessions[member] = (0, "", "", "", temp_message, verify_channel)  # default instantiation
