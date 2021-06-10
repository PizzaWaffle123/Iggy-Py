import os

import discord
import cgh
import json

tracked_polls = {}


class Poll:
    def __init__(self, options, prompt):
        self.results = {}
        self.voters = []
        self.prompt = prompt
        for opt in options:
            self.results[opt] = 0

    def from_json(self, data):
        self.results = data["results"]
        self.voters = data["voters"]
        self.prompt = data["prompt"]

    def to_json(self):
        data = {"results": self.results, "voters": self.voters, "prompt": self.prompt}
        return data

    def cast_vote(self, option, caster):
        # Returns true if the vote was successfully cast
        # Returns false if the specified option is not present in the poll OR if the caster already voted
        if option in self.results.keys() and caster.id not in self.voters:
            self.results[option] += 1
            self.voters.append(caster.id)
            return True
        else:
            return False

    def get_total_votes(self):
        votesum = 0
        for opt in self.results.keys():
            votesum += self.results[opt]
        return votesum

    def get_percentages(self):
        # Returns a dictionary in the form option:percentage
        # Percentage is represented as a string
        total = self.get_total_votes()
        percentages = {}
        for opt in self.results.keys():
            if total == 0:
                portion = 0
            else:
                portion = self.results[opt] / total
            portion_percentage = "%s" % str(portion * 100)
            percentages[opt] = portion_percentage
        return percentages


async def track_new_poll(message, options, prompt):
    new_poll = Poll(options, prompt)
    tracked_polls[message] = new_poll

    percentage_dict = tracked_polls[message].get_percentages()
    resp_embed = discord.Embed()
    resp_embed.set_author(name="Poll Results")
    resp_embed.title = tracked_polls[message].prompt
    for opt in percentage_dict.keys():
        resp_embed.add_field(name=opt + " (%d)" % tracked_polls[message].results[opt],
                             value=percentage_dict[opt] + "%",
                             inline=False)
    resp_embed.set_footer(text="Poll ID: %s" % str(message.id))
    resp_embed.colour = discord.Colour(4171755)

    await message.edit(content=None, embed=resp_embed)

    with open("polls/%s.json" % message.id, "w") as jsonfile:
        json.dump(tracked_polls[message].to_json(), jsonfile)


async def end_poll(message_id):
    global tracked_polls
    found_message = None
    for message in tracked_polls.keys():
        if str(message.id) == message_id:
            found_message = message
            break
    if found_message is None:
        return False
    found_message = await cgh.guild.get_channel(int(found_message.channel.id)).fetch_message(message_id)
    embed_to_edit = found_message.embeds[0]
    embed_to_edit.set_author(name="Poll Results - CLOSED")
    embed_to_edit.colour = discord.Colour(15158332)
    await found_message.edit(embed=embed_to_edit, view=None)
    del tracked_polls[found_message]
    if os.path.exists("./polls/%s.json" % message_id):
        os.remove("./polls/%s.json" % message_id)
    else:
        print("Poll file not found. All good though.")
    return True


async def handle_interaction(interaction):
    print(tracked_polls)

    if interaction.message not in tracked_polls:
        print("Invalid message!")
        return
    print("Valid poll response!")

    if tracked_polls[interaction.message].cast_vote(interaction.data["custom_id"], interaction.user):
        await interaction.response.send_message(ephemeral=True, content="You have successfully cast your vote!")
    else:
        await interaction.response.send_message(ephemeral=True, content="We were unable to cast your vote - "
                                                                  "you likely already voted!")

    percentage_dict = tracked_polls[interaction.message].get_percentages()
    resp_embed = discord.Embed()
    resp_embed.set_author(name="Poll Results")
    resp_embed.title = tracked_polls[interaction.message].prompt
    for opt in percentage_dict.keys():
        resp_embed.add_field(name=opt + " (%d)" % tracked_polls[interaction.message].results[opt],
                             value=percentage_dict[opt] + "%",
                             inline=False)
    resp_embed.set_footer(text="Poll ID: %s" % str(interaction.message.id))
    resp_embed.colour = discord.Colour(4171755)
    await interaction.message.edit(embed=resp_embed)

    with open("polls/%s.json" % interaction.message.id, "w") as jsonfile:
        json.dump(tracked_polls[interaction.message].to_json(), jsonfile)


async def refresh_from_file():
    global tracked_polls
    poll_directory = "./polls"
    for file in os.listdir(poll_directory):
        print(file)
        file = "polls/" + file
        with open(file) as jsonfile:
            data = json.load(jsonfile)
            file = file.split(".")[0]
            file = file.split("/")[1]
            temp_poll = Poll(["Test1", "Test2"], "TestPrompt")
            temp_poll.from_json(data)
            for ch in await cgh.guild.fetch_channels():
                message = None
                if isinstance(ch, discord.TextChannel):
                    try:
                        message = await ch.fetch_message(int(file))
                    except discord.NotFound:
                        message = None
                    finally:
                        if message is not None:
                            break
            if message is None:
                print("Unable to load poll! %s" % file)
            else:
                tracked_polls[message] = temp_poll

