import discord

test_mode = True

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    new_activity = discord.Game(name="around in Python...")
    print(f"Logged in as {client.user}")
    await client.change_presence(activity=new_activity)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")

if __name__ == "__main__":

    token_path = "token_test.txt" if test_mode else "token_main.txt"

    with open(token_path) as fs:
        token = fs.read()

    client.run(token)
    print("Hello world!")
