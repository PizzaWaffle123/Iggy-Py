import datetime

import discord

import database


def ordinal_num(n):
    return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(4 if 10 <= n % 100 < 20 else n % 10, "th")


def verify_intro() -> discord.Embed:
    """

    :return: A discord.Embed containing a small piece of introductory text.
    """
    embed = discord.Embed()
    embed.colour = discord.Colour(10444272)
    embed.title = "Welcome to the Crusader Gaming Hub!"
    embed.description = """
    This server is run by the Gaming & Esports Club at the College of the Holy Cross.
    
    If you're looking to engage with other gamers, you've come to the right place!
    
    To get started, please select the option that best describes you from the dropdown below. 
    """

    return embed


def welcome_embed(member: discord.User, intro: str) -> discord.Embed:
    """
    :param member: The member being welcomed.
    :param intro: The member's short introduction, if applicable.
    :return: A discord.Embed with the member's information and a randomized greeting.
    """
    embed = discord.Embed()
    embed.colour = discord.Colour(10444272)

    count = database.count_table("users")
    ordinal = ordinal_num(count)
    name = member.name

    title = database.random_entry("welcome_titles")
    body = database.random_entry("welcome_bodies")

    title = title.format(count=count, ordinal=ordinal, name=name)
    body = body.format(count=count, ordinal=ordinal, name=name)

    embed.description = body

    # body += "\n\n**Profile: {}**".format(member.mention)

    embed.title = title
    # full_name = member.name + "#" + member.discriminator
    # embed.add_field(name=full_name, value=body, inline=False)
    embed.set_thumbnail(url=member.avatar.url)

    # footer = "**Profile: {}**".format(member.mention)
    # embed.set_footer(text=footer)
    print(intro)

    if intro is not None:
        embed.add_field(name="Introduction", value=intro, inline=True)

    embed.add_field(name="Profile", value=member.mention, inline=True)

    return embed


def manual_verify_embed(member: discord.User, name: str, explanation: str) -> discord.Embed:
    """
    :param member: The user requesting manual verification.
    :param name: The user's provided name.
    :param explanation: The user's provided explanation.
    :return: A discord.Embed containing the member's information, including provided name and explanation.
    """
    embed = discord.Embed()
    embed.colour = discord.Colour(16295218)

    embed.title = f"{member.name}#{member.discriminator}"
    embed.add_field(
        name="Full Name",
        value=name,
        inline=True
    )
    embed.add_field(
        name="Explanation",
        value=explanation,
        inline=True
    )
    embed.set_thumbnail(
        url=member.avatar.url
    )

    embed.timestamp = datetime.datetime.now()
    return embed
