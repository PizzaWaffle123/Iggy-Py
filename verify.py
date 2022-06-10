import os
import random
import re
from discord import Interaction, TextStyle, ui
import smtplib
import ssl

import iggy_ui
from welcome import get_welcome_embed

from dotenv import load_dotenv


security_code_dict = {}


def random_code(length):
    # Generates a random numerical code with provided length, and returns it as a string.
    code = ""
    for i in range(length):
        code += str(random.randint(0, 9))
    return code


def email_is_valid(supplied_email):
    # Checks if the given email is a Holy Cross email.
    regex = "[a-zA-Z]{2,6}[0-9]{2}@(g\.){0,1}holycross\.edu"
    if re.match(regex, supplied_email): return True
    return False


def send_code(user_email, code):
    load_dotenv()
    # Actually sends the verification email.
    port = 465
    context = ssl.create_default_context()
    password = os.getenv('email_password')
    email = "noreply.iggybot@gmail.com"
    message = """Subject: Security Code\n\n
    Hey there Crusader!\n
    Your verification code for the Crusader Gaming Hub is: {code}\n
    Please provide the code to Iggy, and you'll get access to the server. Thanks!\n\n
    (This bot maintained by the Holy Cross Gaming & Esports Club.)"""
    
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(email, password)
        local_message = message.format(code=code)
        server.sendmail(email, user_email, local_message)


def check_code(interaction):
    global security_code_dict
    print(interaction.data)
    submitted_code = interaction.data["custom_id"]

    if security_code_dict[interaction.user.id] == submitted_code:
        return True
    return False


class StudentEmailModal(ui.Modal, title="Student Verification: Email Address"):

    input = ui.TextInput(
        custom_id='email',
        label='enter your Holy Cross email address',
        style=TextStyle.short,
        placeholder="jmsmit25@g.holycross.edu",
        required=True,
        max_length=24,
        )

    async def on_submit(self, interaction: Interaction):
        print("Responding to modal submission...")
        email = interaction.data['components'][0]['components'][0]['value']
        if not email_is_valid(email):
            await interaction.response.send_message(
                ephemeral=True,
                content="Sorry, that's not a valid email address. Please try again."
            )
            return
        code = random_code(6)
        user_id = interaction.user.id
        security_code_dict[user_id] = code
        send_code(email, code)

        codes = [code]
        while len(codes) < 5:
            codes.append(random_code(6))

        codeview = iggy_ui.SecurityCode(codes)
        print("Created codeview...")

        await interaction.response.send_message(
            content="Filler content.",
            view=codeview,
            ephemeral=True
        )


class StudentIntroModal(ui.Modal, title="Student Verification: Introduction"):

    input = ui.TextInput(
        custom_id='intro',
        label='finally, give us a brief intro (optional)',
        style=TextStyle.long,
        placeholder="Hi, my name is John! I'm a sophomore and play lots of Valorant and Minecraft. Let's game sometime!", 
        required=False,
        max_length=200,
        )
    
    async def on_submit(self, interaction: Interaction):
        intro = interaction.data['components'][0]['components'][0]['value']
        if intro == "":
            intro = None
        embed = get_welcome_embed(interaction.user, intro)
        await interaction.response.send_message(embeds=[embed])
