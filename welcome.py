# VERSION 3.0 UPGRADE PROJECT
# STATUS: COMPLETE (Ready For 3.0)

import random
import discord
import cgh


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
    "A NEW GAMER ENTERS THE GAMER ZONE",
    "SO, YOU WANT TO HEAR ANOTHER STORY, EH?",
    "NOW ABOUT THAT BEER I OWED YA!",
    "YOU ARE NOW ON THE PURPLE TEAM",
    "A NEW FIGHTER HAS JOINED THE BATTLE",
    "HEY - YOU'RE FINALLY AWAKE",
    "SO - WHO'S READY TO MAKE SOME SCIENCE?",
    "KIROV REPORTING",
    "AIN'T THAT A KICK IN THE HEAD",
    "LEVEL UP: {count}",
    "HI THERE NEIGHBOR",
    "WE'VE BEEN EXPECTING YOU, {name}"
]

# Note: Anywhere that {count} is shown will be formatted out to include the count parameter in the get_welcome_embed
# function. {count} will only get formatted as the number itself, it WILL NOT become ordinal (1st, 2nd, 3rd, etc.).
# If you add any new bodies, you do not need to include {count}.
# UPDATE 25 MAY 2021 - The formatter {ordinal} is now supported.
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
    "Welcome welcome Number {count}!",
    "Our {ordinal} member!",
    "{name}, Rush Chairman, damn glad to meet ya!"
]


def get_welcome_embed(member):
    # Returns an embed which can then be sent in a message.
    # Working with embeds is really fun and should be self-explanatory.
    embed = discord.Embed()
    embed.colour = discord.Colour(10444272)

    formatting_dictionary = {"count": cgh.count_members(),
                             "ordinal": ordinal(cgh.count_members()),
                             "name": member.name}

    title = random.choice(welcome_titles)
    title = title.format(**formatting_dictionary)

    body = random.choice(welcome_bodies)
    body = body.format(**formatting_dictionary)

    body = body + "\n\n**Profile: {}**".format(member.mention)

    embed.title = title
    full_name = member.name + "#" + member.discriminator
    embed.add_field(name=full_name, value=body, inline=False)
    embed.set_thumbnail(url=member.avatar.url)

    return embed


def ordinal(n):
    return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(4 if 10 <= n % 100 < 20 else n % 10, "th")
