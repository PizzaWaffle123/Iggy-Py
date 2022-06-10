import discord

import database


def ordinal_num(n):
    return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(4 if 10 <= n % 100 < 20 else n % 10, "th")


def get_welcome_embed(member, intro=None):
    # Returns an embed which can then be sent in a message.
    # Working with embeds is really fun and should be self-explanatory.
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


