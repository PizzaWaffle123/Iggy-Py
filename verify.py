import os
import random
import re
from discord import Interaction, TextStyle, ui
import smtplib
import ssl
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
    if re.match(regex, supplied_email) : return True
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


class student_email_modal(ui.Modal, title="Student Verification"):

    input = ui.TextInput(
        custom_id='email',
        label='enter your Holy Cross email address',
        style=TextStyle.short,
        placeholder="jmsmit25@g.holycross.edu",
        required=True,
        max_length=25,
        )

    async def on_submit(self, interaction: Interaction):
        email = interaction.data['components'][0]['components'][0]['value']
        if not email_is_valid(email) : return
        code = random_code(6)
        user_id = interaction.user.id
        security_code_dict[user_id] = code
        send_code(email, code)

        await interaction.response.send_modal(student_code_modal())


class student_code_modal(ui.Modal, title="Student Verification"):

    input = ui.TextInput(
        custom_id='code',
        label='enter your security code',
        style=TextStyle.short,
        placeholder="123456",
        required=True,
        max_length=6,
        )
    
    async def on_submit(self, interaction: Interaction):
        code = interaction.data['components'][0]['components'][0]['value']
        user_id = interaction.user.id
        if code == security_code_dict[user_id] : 
            # remove Pending
            # add Crusader
            # add Class Year (post parse)
            await interaction.response.send_modal(student_intro_modal())


class student_intro_modal(ui.Modal, title="Student Verification"):

    intro = ui.TextInput(
        custom_id='intro',
        label='finally, give us a brief intro (optional)',
        style=TextStyle.long,
        placeholder="Hi, my name is John! I'm a sophomore and play lots of Valorant and Minecraft. Let's game sometime!", 
        required=False,
        max_length=200,
        )
    
    async def on_submit(self, interaction: Interaction):
        intro = interaction.data['components'][0]['components'][0]['value']
        embed = get_welcome_embed(interaction.user, intro)
        await interaction.response.send_message(embeds=[embed])