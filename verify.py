import code
import email
from discord import Interaction, TextStyle, ui

class student_email_modal(ui.Modal, title="Student Verification"):

    input = ui.TextInput(
        custom_id='email',
        label='enter your Holy Cross email address',
        style=TextStyle.short,
        placeholder="jmsmit25@g.holycross.edu",
        required=True,
        max_length=25,
        )
    intro = ui.TextInput(
        custom_id='intro',
        label='give us a brief intro (optional)',
        style=TextStyle.long,
        placeholder="Hi, my name is John! I'm a sophomore and play lots of Valorant and Minecraft. Let's game sometime!", 
        required=False,
        max_length=200,
        )
    
    async def on_submit(self, interaction: Interaction):
        email = interaction.data['components'][0]['components'][0]['value']
        intro = interaction.data['components'][1]['components'][0]['value']
        print('Email: ', email)
        print('Intro: ', intro)
        await interaction.response.send_message('Thanks for your response!', ephemeral=True)