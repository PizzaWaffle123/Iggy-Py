import discord
import cgh
import welcome
import verify

client = discord.Client(intents=discord.Intents.all())
my_cgh = None


@client.event
async def on_ready():
    global my_cgh
    print('Logged on as {0}!'.format(client.user))
    my_cgh = cgh.CGH(client.guilds[0])


@client.event
async def on_member_join(member):
    global my_cgh
    await my_cgh.new_user(member)
    await verify.new_session(member)


@client.event
async def on_user_update(before, after):
    before_name = "%s#%s" % (before.name, before.discriminator)
    after_name = "%s#%s" % (after.name, after.discriminator)
    if before_name != after_name:
        await my_cgh.username_update(before, after)


@client.event
async def on_member_update(before, after):
    before_roles = set(before.roles)
    after_roles = set(after.roles)
    role_changed = after_roles - before_roles
    if my_cgh.role_crusader in role_changed:
        print("The Crusader role was appended to somebody!")
        await my_cgh.channel_general.send(embed=welcome.get_welcome_embed(after, my_cgh.count_members()))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        results = verify.new_dm_input(message.author, message.content)
        if results[0] == 2:
            await my_cgh.verify_user(message.author, results[1])

    if message.content.startswith("$count"):
        await message.channel.send("%d" % my_cgh.count_members())
    elif message.content.startswith("$test"):
        message_parts = message.content.split(" ")
        if len(message_parts) < 2:
            return
        if message_parts[1] == "verify":
            await verify.new_session(message.author)


client.activity = discord.Activity(name="Evo tear his hair out", type=discord.ActivityType.watching)
# verify.send_code("ejfear21@g.holycross.edu", "test")

client.run("NzcxODAwMjA3NzMzNjg2Mjg0.X5xY9A.Zefj_2DQSTRS3lMPyXOFpfB0V4A")
