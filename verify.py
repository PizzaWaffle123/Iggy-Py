import discord
from discord import Interaction, TextStyle, ui

class student_modal(ui.Modal, title="Verify Your Identity"):
    email = ui.TextInput(
        label="enter your Holy Cross email address",
        style=TextStyle.short,
        placeholder="jmsmit25@g.holycross.edu",
        required=True,
        max_length=25,
        )
    intro = ui.TextInput(
        label="give us a brief intro (optional)",
        style=TextStyle.paragraph,
        placeholder="Hi, my name is John! I'm a sophomore and play lots of Valorant and Minecraft. Let's game sometime!", 
        required=False,
        max_length=200,
        )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message('Thanks for your response!', ephemeral=True)


