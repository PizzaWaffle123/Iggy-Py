import smtplib
import ssl
import random
import discord
import json

color_okay = discord.Colour(4171755)      # Special Blue
color_err = discord.Colour(15158332)      # Pending Red
color_success = discord.Colour(3066993)   # Event Green
color_waiting = discord.Colour(16295218)  # Gamer Orange

# Anything prefixed with em_ is an embed object, to be sent in a message.
# You can see what the embeds are used for by reading their contents - should be pretty clear.

em_stage0 = discord.Embed()  # Welcome to CGH! Please enter your email!\
em_stage0.title = "Welcome to the Crusader Gaming Hub!"
em_stage0.description = "Before you can access the server, you'll need to verify yourself as a Holy Cross student.\n" \
                        "**Please enter your @g.holycross.edu email address below.**\n" \
                        "*If you would like to request a Guest Pass, simply say \"guest\".*\n" \
                        "*If you are a prospective student (class of 2025), simply say \"2025\".*"
em_stage0.colour = color_okay

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

active_sessions = {}  # dictionary in format member:(stage,code,email,classyear,menu_message)
# stage is int, menu_message is message, all others are string
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

new_user_queue = []

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


async def guest_issue(member, approval):
    # Notifies user if their Guest Pass has been approved or denied.
    if approval is True:
        await active_sessions[member][4].edit(embed=get_embed_by_name("stage9_guest"))
    else:
        await active_sessions[member][4].edit(embed=get_embed_by_name("stage4_denied"))
    del active_sessions[member]


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
        elif u_input_react.emoji == "⚪":
            # White Circle - GUEST
            print("Guest!")
        elif u_input_react.emoji == "🟡":
            # Yellow Circle - PROSPECTIVE
            print("Prospective!")
        elif u_input_react.emoji == "🔵":
            # Blue Circle - ALUM
            print("Alum!")
        else:
            return

        await member_vs[4].edit(embed=get_embed_by_name("TEST"))
        await member_vs[4].clear_reactions()


async def new_session(member):
    global active_sessions
    # Used to initiate a verification session over DMs with a user.
    # We call this function whenever someone new joins CGH.
    if member.dm_channel is None:
        await member.create_dm()
    print("Starting new session...")
    temp_message = await member.dm_channel.send(embed=get_embed_by_name("stage0"))
    await temp_message.add_reaction("🟣")
    await temp_message.add_reaction("⚪")
    await temp_message.add_reaction("🟡")
    await temp_message.add_reaction("🔵")
    active_sessions[member] = (0, "", "", "", temp_message)  # default instantiation
