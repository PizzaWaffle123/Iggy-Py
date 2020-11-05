import random
import discord

welcome_titles = [
    "NEW CHALLENGER APPROACHING",
    "NEW MEMBER INCOMING",
    "FRESH MEAT",
    "NEW MEMBER ALERT",
    "A NEW PLAYER HAS JOINED",
    "HOWDY PARTNER",
    "YOU HAVE ENTERED A PVP-ENABLED ZONE",
    "A NEW HAND TOUCHES THE BEACON",
    "YOU HAVE BEEN AUTOBALANCED",
    "THE CREATURES OF PANDORA GROW STRONGER",
    "RISE AND SHINE, MR. FREEMAN",
    "INSERT COIN TO CONTINUE",
    "PRESS ANY KEY TO CONTINUE",
    "A NEW GAMER ENTERS THE GAMER ZONE"
]

welcome_bodies = [
    "Say \"hi\" to number {count}!",
    "Now the server's at {count} members!",
    "Ready Player {count}!",
    "Player {count}, press any button to continue!",
    "Congratulations, you are lucky number {count}!\nClaim your free iPhone 11 now!",
    "Now Serving: {count}",
    "{count}! It's a magic number!",
    "{count} members? That's crazy!",
    "{count} members? That's actually insane!",
    "Welcome welcome Number {count}!"
]


def get_welcome_embed(member, count):
    embed = discord.Embed()
    embed.colour = discord.Colour.from_rgb(136, 38, 204)
    title = random.choice(welcome_titles)
    body = random.choice(welcome_bodies)
    body = body.format(count=count)

    embed.title = title
    full_name = member.name + "#" + member.discriminator
    embed.add_field(name=full_name, value=body, inline=False)
    embed.set_thumbnail(url=member.avatar_url)

    return embed
