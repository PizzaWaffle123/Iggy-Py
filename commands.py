import discord
import database
import iggy_ui
import sound
from iggy_ui import MenuVerify
import welcome as welc


@discord.app_commands.command(name="test", description="Tests things.")
async def co_test(interaction: discord.Interaction):
    await interaction.response.send_message(
        content="Test!"
    )


@discord.app_commands.command(name="sql", description="Submits a raw SQL query and returns the results.")
@discord.app_commands.describe(query="Your raw SQL query.")
async def co_sql(interaction: discord.Interaction, query: str):
    print("Processing query...")
    await interaction.response.send_message(database.raw_query(query))


@discord.app_commands.command(name="welcome", description="Generates a welcome embed.")
async def co_welcome(interaction: discord.Interaction):
    await interaction.response.send_message(
        embeds=[welc.get_welcome_embed(interaction.user, "Test introduction!")]
    )


@discord.app_commands.command(name="modal", description="Supplies a modal to the user.")
async def co_modal(interaction: discord.Interaction):
    await interaction.response.send_message(
        content="Not ready yet!"
    )


@discord.app_commands.command(name="dbupdate", description="DB update!")
async def co_dbupdate(interaction: discord.Interaction):
    print("DB update!")
    # member_iter = interaction.guild.fetch_members()
    await interaction.response.defer(ephemeral=True, thinking=True)
    discord_members = interaction.guild.members
    print(len(discord_members))
    rows = 0
    async for user in interaction.guild.fetch_members():
        userdata = database.identify_user(user.id)
        if user.bot:
            continue
        if userdata is None:
            # The user is not in the database.
            query = f"INSERT INTO users (user_id, username) VALUES ({user.id}, \"{user.name}#{user.discriminator}\")"

        else:
            query = f"UPDATE users SET user_id = {user.id}, username = \"{user.name}#{user.discriminator}\" " \
                    f"WHERE user_id = {user.id}"
        database.raw_query(query)
        rows += 1
    await interaction.followup.send(
        content=f"Done - {rows} rows affected."
    )


@discord.app_commands.command(name="graduate", description="Converts all eligible Students into Alumni.")
async def co_graduate(interaction: discord.Interaction):
    from datetime import datetime
    current_year = datetime.now().year
    query = f"SELECT user_id FROM users WHERE grad_year <= {current_year}"
    db_users = database.raw_query(query)
    print(db_users)
    for user in db_users:
        """
        This loop should:
        - Get the user by their ID.
        - If they don't have the Alumni role, apply it.
        - Reply to the command runner with the number of users affected.
        """
        graduate_id = user[0]
        print(graduate_id)

    await interaction.response.send_message(
        ephemeral=True,
        content=f"Eligible Users: {len(db_users)}"
    )


@discord.app_commands.command(name="sound", description="Attempts to play a sound effect from the files.")
async def co_sound(interaction: discord.Interaction, soundstr: str):
    await sound.play(soundstr)
    await interaction.response.send_message(
        ephemeral=True,
        content="Sure man, no problem."
    )


@discord.app_commands.command(name="testdropdown", description="Summons a test dropdown.")
async def co_testdropdown(interaction: discord.Interaction):
    mv = iggy_ui.MenuVerify()
    await interaction.response.send_message(
        content="Filler content.",
        view=mv
    )


@discord.app_commands.context_menu(name="Identify")
async def ca_user_identify(interaction: discord.Interaction, user: discord.Member):
    user_data = database.identify_user(user.id)
    """
        user_data now contains a 5-tuple with the following values:
        - User ID
        - User full name
        - User grad year
        - User email stub
        - Username#Discriminator
    """
    data_embed = discord.Embed()
    data_embed.set_author(name="User Information")
    data_embed.title = f"{user.name}#{user.discriminator}"

    if user_data is None or len(user_data) == 0:
        data_embed.description = "No information available on this user!\n Please let the E-Board know!"
    else:
        data_embed.add_field(name="Name", value=user_data[1])
        data_embed.add_field(name="Class", value=user_data[2])
        data_embed.add_field(name="Email", value=user_data[3] + "@g.holycross.edu", inline=False)

    data_embed.set_thumbnail(url=user.avatar.url)
    data_embed.colour = 16777215

    await interaction.response.send_message(
        ephemeral=True,
        embeds=[data_embed]
    )


@discord.app_commands.context_menu(name="Esports Management")
async def ca_user_esports(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(
        ephemeral=True,
        content=f"Not implemented yet! Used interaction on {user.name}#{user.discriminator}"
    )


@discord.app_commands.context_menu(name="Thumbs")
async def ca_message_thumbs(interaction: discord.Interaction, message: discord.Message):
    await message.add_reaction("👍")
    await interaction.response.send_message(
        ephemeral=True,
        content="Done!"
    )
