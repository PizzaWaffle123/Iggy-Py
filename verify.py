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

year_senior = "2022"
year_junior = "2023"
year_sophomore = "2024"
year_freshman = "2025"
year_prospective = "2026"


def get_embed_by_name(name, info):
    rawname = name
    name = "embeds/" + name + ".json"
    with open(name) as jsonfile:
        data = json.load(jsonfile)
    if rawname == "stage3" or rawname == "stage8":
        data = parse_email_into_embed(data, info)
    if rawname == "stage1":
        data = parse_active_years(data)
    if rawname == "stage6":
        data = parse_alum_years(data)
    if rawname == "stage7":
        data = parse_gradyear_into_embed(data, info)
    return discord.Embed.from_dict(data)


def parse_email_into_embed(data, student_email):
    string_to_parse = data["fields"][0]["value"]
    string_to_parse = string_to_parse.format(student_email)
    data["fields"][0]["value"] = string_to_parse
    return data


def parse_gradyear_into_embed(data, gradyear):
    string_to_parse = data["fields"][1]["value"]
    string_to_parse = string_to_parse.format(gradyear)
    data["fields"][1]["value"] = string_to_parse
    return data


def parse_active_years(data):
    upperclass = data["fields"][0]["value"]
    underclass = data["fields"][1]["value"]

    upperclass = upperclass.format(year_senior, year_junior)
    underclass = underclass.format(year_sophomore, year_freshman)

    data["fields"][0]["value"] = upperclass
    data["fields"][1]["value"] = underclass
    return data


def parse_alum_years(data):
    senior_num = int(year_senior)
    leftside = data["fields"][0]["value"]
    rightside = data["fields"][1]["value"]

    leftside = leftside.format(senior_num-1, senior_num-2, senior_num-3)
    rightside = rightside.format(senior_num-4, senior_num-5, senior_num-6)

    data["fields"][0]["value"] = leftside
    data["fields"][1]["value"] = rightside
    return data


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


async def new_input(member, u_input_str, u_input_react, origin_channel, raw_message):
    global active_sessions
    # Returns a Tuple (user stage, response info)
    # This function happens whenever a user reacts or says something in the DM channel.
    # u_input_str is whatever the user typed, u_input_react is the Reaction event if applicable.
    # either of these values can be None, but one must always be non-None.
    if member not in active_sessions.keys():
        return -1
    member_vs = active_sessions[member]  # vs stands for "verify state", see above
    if u_input_react is None and u_input_str is None:
        # We should...never be here. Time to panic.
        return -1
    if origin_channel != member_vs[5]:
        return -1

    if member_vs[0] == 0:
        # User has picked their group.
        if u_input_react.emoji == "🟣":
            # Purple Circle - STUDENT
            print("Student!")
            active_sessions[member] = (1, member_vs[1], member_vs[2], member_vs[3], member_vs[4], member_vs[5])
            await active_sessions[member][4].edit(embed=get_embed_by_name("stage1", "null"))
            await member_vs[4].clear_reactions()

            await member_vs[4].add_reaction("🇦")
            await member_vs[4].add_reaction("🇧")
            await member_vs[4].add_reaction("🇨")
            await member_vs[4].add_reaction("🇩")
        elif u_input_react.emoji == "⚪":
            # White Circle - GUEST
            print("Guest!")
            active_sessions[member] = (4, member_vs[1], member_vs[2], member_vs[3], member_vs[4], member_vs[5])
            await active_sessions[member][4].edit(embed=get_embed_by_name("stage4", "null"))
            await member_vs[4].clear_reactions()
            await cgh.generate_verify_request(member, "guest", "Test", "I am testing a Guest Pass!")
        elif u_input_react.emoji == "🟡":
            # Yellow Circle - PROSPECTIVE
            print("Prospective!")
            active_sessions[member] = (5, member_vs[1], member_vs[2], member_vs[3], member_vs[4], member_vs[5])
            await active_sessions[member][4].edit(embed=get_embed_by_name("stage5", "null"))
            await member_vs[4].clear_reactions()
        elif u_input_react.emoji == "🔵":
            # Blue Circle - ALUM
            print("Alum!")
            active_sessions[member] = (6, member_vs[1], member_vs[2], member_vs[3], member_vs[4], member_vs[5])
            await active_sessions[member][4].edit(embed=get_embed_by_name("stage6", "null"))
            await member_vs[4].clear_reactions()

            await member_vs[4].add_reaction("🇦")
            await member_vs[4].add_reaction("🇧")
            await member_vs[4].add_reaction("🇨")
            await member_vs[4].add_reaction("🇩")
            await member_vs[4].add_reaction("🇪")
            await member_vs[4].add_reaction("🇫")
        else:
            return -1
    elif member_vs[0] == 1:
        # User has picked their class year.
        if u_input_react.emoji == "🇦":
            active_sessions[member] = (2, member_vs[1], member_vs[2], year_senior, member_vs[4], member_vs[5])
            await active_sessions[member][4].edit(embed=get_embed_by_name("stage2", "null"))
            await member_vs[4].clear_reactions()
        elif u_input_react.emoji == "🇧":
            active_sessions[member] = (2, member_vs[1], member_vs[2], year_junior, member_vs[4], member_vs[5])
            await active_sessions[member][4].edit(embed=get_embed_by_name("stage2", "null"))
            await member_vs[4].clear_reactions()
        elif u_input_react.emoji == "🇨":
            active_sessions[member] = (2, member_vs[1], member_vs[2], year_sophomore, member_vs[4], member_vs[5])
            await active_sessions[member][4].edit(embed=get_embed_by_name("stage2", "null"))
            await member_vs[4].clear_reactions()
        elif u_input_react.emoji == "🇩":
            active_sessions[member] = (2, member_vs[1], member_vs[2], year_freshman, member_vs[4], member_vs[5])
            await active_sessions[member][4].edit(embed=get_embed_by_name("stage2", "null"))
            await member_vs[4].clear_reactions()
        else:
            return -1
    elif member_vs[0] == 2:
        # User has entered an email address.
        if u_input_str is None:
            return -1
        await raw_message.delete()
        if not email_is_valid(u_input_str):
            return -1
        user_email = u_input_str
        code = random_code(8)
        send_code(user_email, code)
        active_sessions[member] = (3, code, user_email, member_vs[3], member_vs[4], member_vs[5])
        await active_sessions[member][4].edit(embed=get_embed_by_name("stage3", user_email))
        await member_vs[4].clear_reactions()
        await member_vs[4].add_reaction("🔄")
        await member_vs[4].add_reaction("❌")
    elif member_vs[0] == 3:
        # User has EITHER input a verification code or used a reaction.
        if u_input_str is None:
            # This means the input was a reaction.
            if u_input_react.emoji == "🔄":
                # User requested code to be resent.
                code = random_code(8)
                send_code(member_vs[2], code)
                active_sessions[member] = (member_vs[0], code, member_vs[2], member_vs[3], member_vs[4], member_vs[5])
                await active_sessions[member][4].edit(embed=get_embed_by_name("stage3", member_vs[2]))
                await member_vs[4].clear_reactions()
                await member_vs[4].add_reaction("🔄")
                await member_vs[4].add_reaction("❌")
            elif u_input_react.emoji == "❌":
                # User requested to re-enter their email address.
                active_sessions[member] = (2, member_vs[1], member_vs[2], member_vs[3], member_vs[4], member_vs[5])
                await active_sessions[member][4].edit(embed=get_embed_by_name("stage2", "null"))
                await member_vs[4].clear_reactions()
        elif u_input_react is None:
            # The input was a string.
            real_code = member_vs[1]
            entered_code = u_input_str
            await raw_message.delete()
            if real_code != entered_code:
                await active_sessions[member][4].edit(embed=get_embed_by_name("stage3_failure", member_vs[2]))
            else:
                await active_sessions[member][4].edit(embed=get_embed_by_name("stage9_student", member_vs[2]))
                await member_vs[4].clear_reactions()
                await cgh.verify_user(member, member_vs[2], member_vs[3])
                await session_cleanup(member)
        else:
            return -1
    elif member_vs[0] == 5:
        # User should have entered their full name.
        if u_input_str is None:
            return -1
        full_name = u_input_str
        await raw_message.delete()
        await cgh.log_prospective(member, full_name, year_prospective)
        await active_sessions[member][4].edit(embed=get_embed_by_name("stage9_prospective", member_vs[2]))
        await session_cleanup(member)
    elif member_vs[0] == 6:
        # User selected an alum graduation year or entered one.

        grad_year = "1"

        if u_input_str is None:
            # User used a reaction.
            if u_input_react.emoji == "🇦":
                grad_year = str(int(year_senior)-1)
            elif u_input_react.emoji == "🇧":
                grad_year = str(int(year_senior) - 2)
            elif u_input_react.emoji == "🇨":
                grad_year = str(int(year_senior) - 3)
            elif u_input_react.emoji == "🇩":
                grad_year = str(int(year_senior) - 4)
            elif u_input_react.emoji == "🇪":
                grad_year = str(int(year_senior) - 5)
            elif u_input_react.emoji == "🇫":
                grad_year = str(int(year_senior) - 6)
            else:
                return -1
        else:
            await raw_message.delete()
            # User entered a graduation year
            grad_year = u_input_str
        active_sessions[member] = (7, member_vs[1], member_vs[2], grad_year, member_vs[4], member_vs[5])
        await active_sessions[member][4].edit(embed=get_embed_by_name("stage7", grad_year))
        await member_vs[4].clear_reactions()
        await member_vs[4].add_reaction("🔴")
    elif member_vs[0] == 7:
        if u_input_str is None:
            # User used a reaction.
            if u_input_react.emoji == "🔴":
                active_sessions[member] = (7.5, member_vs[1], member_vs[2], member_vs[3], member_vs[4], member_vs[5])
                await active_sessions[member][4].edit(embed=get_embed_by_name("stage_7b", "null"))
                await member_vs[4].clear_reactions()
            else:
                return -1
        else:
            # User entered text.
            await raw_message.delete()
            if not email_is_valid(u_input_str):
                return -1
            user_email = u_input_str
            code = random_code(8)
            send_code(user_email, code)
            active_sessions[member] = (8, code, user_email, member_vs[3], member_vs[4], member_vs[5])
            await active_sessions[member][4].edit(embed=get_embed_by_name("stage8", user_email))
            await member_vs[4].clear_reactions()
            await member_vs[4].add_reaction("🔄")
            await member_vs[4].add_reaction("❌")
    elif member_vs[0] == 7.5:
        if u_input_str is None:
            return -1
        await raw_message.delete()
        full_name = u_input_str
        active_sessions[member] = (7.75, member_vs[1], member_vs[2], member_vs[3], member_vs[4], member_vs[5])
        await active_sessions[member][4].edit(embed=get_embed_by_name("stage_7c", "null"))
        await member_vs[4].clear_reactions()
        await cgh.notify_of_alum(member, full_name, member_vs[3])
    elif member_vs[0] == 8:
        if u_input_str is None:
            # This means the input was a reaction.
            if u_input_react.emoji == "🔄":
                # User requested code to be resent.
                code = random_code(8)
                send_code(member_vs[2], code)
                active_sessions[member] = (member_vs[0], code, member_vs[2], member_vs[3], member_vs[4], member_vs[5])
                await active_sessions[member][4].edit(embed=get_embed_by_name("stage8", member_vs[2]))
                await member_vs[4].clear_reactions()
                await member_vs[4].add_reaction("🔄")
                await member_vs[4].add_reaction("❌")
            elif u_input_react.emoji == "❌":
                # User requested to re-enter their email address.
                active_sessions[member] = (7, member_vs[1], member_vs[2], member_vs[3], member_vs[4], member_vs[5])
                await active_sessions[member][4].edit(embed=get_embed_by_name("stage7", "null"))
                await member_vs[4].clear_reactions()
        elif u_input_react is None:
            # The input was a string.
            real_code = member_vs[1]
            entered_code = u_input_str
            await raw_message.delete()
            if real_code != entered_code:
                await active_sessions[member][4].edit(embed=get_embed_by_name("stage8_failure", member_vs[2]))
            else:
                await active_sessions[member][4].edit(embed=get_embed_by_name("stage9_alum", member_vs[2]))
                await member_vs[4].clear_reactions()
                await cgh.verify_user(member, member_vs[2], member_vs[3])
                await cgh.log_alum(member, None, member_vs[2], member_vs[3])
                await session_cleanup(member)
        else:
            return -1

    return 0


async def new_session(member):
    global active_sessions
    # Used to initiate a verification session over DMs with a user.
    # We call this function whenever someone new joins CGH.
    print("Starting new session...")
    verify_channel = await cgh.create_verify_session_channel(member)
    temp_message = await verify_channel.send(content=member.mention, embed=get_embed_by_name("stage0", "null"))

    await temp_message.add_reaction("🟣")
    await temp_message.add_reaction("⚪")
    await temp_message.add_reaction("🟡")
    await temp_message.add_reaction("🔵")
    active_sessions[member] = (0, "", "", "", temp_message, verify_channel)  # default instantiation
