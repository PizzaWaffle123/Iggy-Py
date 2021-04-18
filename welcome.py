import random
import discord


# Yes, these are just lists.
# Yes, you can add or remove entries however you please.
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

# Note: Anywhere that {count} is shown will be formatted out to include the count parameter in the get_welcome_embed
# function. {count} will only get formatted as the number itself, it WILL NOT become ordinal (1st, 2nd, 3rd, etc.).
# If you add any new bodies, you do not need to include {count}.
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
    # Returns an embed which can then be sent in a message.
    # Working with embeds is really fun and should be self-explanatory.
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
