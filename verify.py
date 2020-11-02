import smtplib
import ssl
import random
import threading
import discord

color_okay = discord.Colour.from_rgb(136, 38, 204)
color_err = discord.Colour.from_rgb(214, 40, 61)
color_success = discord.Colour.from_rgb(126, 211, 33)
color_pending = discord.Colour.from_rgb(245, 166, 35)

em_stage0 = discord.Embed()  # Welcome to CGH! Please enter your email!\
em_stage0.title = "Welcome to the Crusader Gaming Hub!"
em_stage0.description = "Before you can access the server, you'll need to verify yourself as a Holy Cross student.\n" \
                        "Please enter your @g.holycross.edu email address below. If you would like to request a " \
                        "Guest Pass, simply say \"guest\"."
em_stage0.colour = color_okay

em_stage0_err = discord.Embed() # Invalid email! Try again!
em_stage0_err.title = "Invalid Email Address!"
em_stage0_err.description = "Hmmm, it looks like that isn't a valid Holy Cross email address. Try entering it again."
em_stage0_err.colour = color_err

em_stage1 = discord.Embed()  # Please enter your verification code!
em_stage1.title = "Verification Email Sent!"
em_stage1.description = "Thank you! You should receive a verification code shortly - just send it here when you do!\n" \
                        "If you haven't received a code within a few minutes, you can check your spam folder.\n" \
                        "Alternatively, you can say \"resend\" to send the email again, or \"restart\" to start over."
em_stage1.colour = color_okay

em_stage1_err = discord.Embed()  # Invalid verification code! Try again!
em_stage1_err.title = "Invalid Security Code!"
em_stage1_err.description = "Sorry, that doesn't look like the code I sent you! You can re-enter the code if you think" \
                            "you typed it incorrectly.\nYou can also say \"resend\" to send the code again, " \
                            "or \"restart\" to start over."
em_stage1_err.colour = color_err

em_stage2 = discord.Embed()  # Success!
em_stage2.title = "Success!"
em_stage2.description = "Congratulations! You're now verified in the Crusader Gaming Hub, and you should have access " \
                        "to all channels. Have fun!"
em_stage2.colour = color_success

em_stage3 = discord.Embed()  # Guest Pass awaiting approval
em_stage3.title = "Guest Pass Requested!"
em_stage3.description = "I've notified the moderators that you are requesting a Guest Pass. You'll be notified if " \
                        "your request is accepted or declined. Thank you!"
em_stage3.colour = color_pending

em_stage3_success = discord.Embed()  # Guest Pass approved!
em_stage3_success.title = "Guest Pass Approved!"
em_stage3_success.description = "Congratulations! You've been issued a Guest Pass, and you should now have access " \
                                "to the Crusader Gaming Hub. Have fun!"
em_stage3_success.colour = color_success

em_stage3_failure = discord.Embed()  # Guest Pass declined!
em_stage3_failure.title = "Guest Pass Declined!"
em_stage3_failure.description = "Sorry, but the moderators have not approved your request for a Guest Pass. " \
                                "Please try again another time, or check in with the person who invited you."
em_stage3_failure.colour = color_err


port = 465
password = "dogxbxvpxhdwfyhj"
email = "noreply.iggybot@gmail.com"
message = """\
Subject: Verification Code

Hey there Crusader!\n
Your verification code for the Crusader Gaming Hub is: {code}\n
Please provide the code to Iggy, and you'll get access to the server. Thanks!\n\n

(This bot maintained by the Holy Cross Gaming & Esports Club.)"""

active_sessions = {}  # dictionary in format member:VerifyState


class VerifyState:
    def __init__(self):
        self.code = ""
        self.stage = 0
        self.email = ""
        # Verification Stage Key
        # 0 - User has just joined and needs to enter their email address.
        # 1 - User's email address has been stored, awaiting verification code


new_user_queue = []

context = ssl.create_default_context()


def send_code(user_email, code):
    global message
    global email
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(email, password)
        local_message = message.format(code=code)
        server.sendmail(email, user_email, local_message)


def random_code(length):
    code = ""
    for i in range(length):
        code += str(random.randint(0, 9))
    return code


def email_is_valid(supplied_email):
    if supplied_email.endswith("@g.holycross.edu"):
        return True
    return False


async def guest_issue(member, approval):
    if approval is True:
        await member.dm_channel.send(embed=em_stage3_success)
    else:
        await member.dm_channel.send(embed=em_stage3_failure)
    del active_sessions[member]


async def new_dm_input(member, u_input):
    # Returns a Tuple (user stage, response info)
    if member not in active_sessions.keys():
        return
    member_vs = active_sessions[member]

    if member_vs.stage == 0:
        # User should have entered their email address or "guest" keyword
        u_input = u_input.lower()
        if u_input.startswith("guest"):
            active_sessions[member].stage = 3
            await member.dm_channel.send(embed=em_stage3)
            return 3, "guest"

        elif email_is_valid(u_input):
            active_sessions[member].code = random_code(8)
            active_sessions[member].email = u_input
            active_sessions[member].stage = 1
            send_code(u_input, active_sessions[member].code)
            await member.dm_channel.send(embed=em_stage1)

            return 1, "success"
        else:
            await member.dm_channel.send(embed=em_stage0_err)
            return 0, "failure"
    elif member_vs.stage == 1:
        # User should have entered their verification code or resend/restart
        if u_input.lower() == "resend":
            await member.dm_channel.send(embed=em_stage1)
            send_code(active_sessions[member].email, active_sessions[member].code)
            return 1, "resend"
        elif u_input.lower() == "restart":
            await member.dm_channel.send(embed=em_stage0)
            active_sessions[member].stage = 0
            return 0, "restart"
        elif u_input == member_vs.code:
            await member.dm_channel.send(embed=em_stage2)
            del active_sessions[member]
            return 2, member_vs.email
        else:
            await member.dm_channel.send(embed=em_stage1_err)
            return 1, "failure"
    elif member_vs.stage != 3:
        # If user sends a DM, but their session is already over, just remove their session
        del active_sessions[member]


async def new_session(member):
    new_user_queue.append(member)
    if member.dm_channel is None:
        await member.create_dm()
    print("Starting new session...")
    await member.dm_channel.send(embed=em_stage0)


def verify_listener():
    global active_sessions
    while True:
        while not new_user_queue:
            pass
        print("New user noticed!")
        member = new_user_queue.pop(0)
        active_sessions[member] = VerifyState()



verify_thread = threading.Thread(target=verify_listener)
verify_thread.start()
