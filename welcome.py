import discord

import database


def ordinal_num(n):
    return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(4 if 10 <= n % 100 < 20 else n % 10, "th")


def get_welcome_embed(member):
    # Returns an embed which can then be sent in a message.
    # Working with embeds is really fun and should be self-explanatory.
    embed = discord.Embed()
    embed.colour = discord.Colour(10444272)

    count = database.count_table("students")
    ordinal = ordinal_num(count)
    name = member.name

    title = database.random_entry("welcome_titles")
    body = database.random_entry("welcome_bodies")

    title = title.format(count=count, ordinal=ordinal, name=name)
    body = body.format(count=count, ordinal=ordinal, name=name)

    body += "\n\n**Profile: {}**".format(member.mention)

    embed.title = title
    full_name = member.name + "#" + member.discriminator
    embed.add_field(name=full_name, value=body, inline=False)
    embed.set_thumbnail(url=member.avatar.url)

    return embed


if __name__ == "__main__":
    # For migrating all old welcome messages into database.
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
        "{name}, Rush Chairman, damn glad to meet ya!",
        "Yep. {count}! That's what is says on the sheet.",
        "{count} members? That's a lot of people!"
    ]
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

    for message in welcome_bodies:
        database.raw_query(f"INSERT INTO welcome_bodies (message) VALUES (\"{message}\")")
        print("Added %s" % message)

