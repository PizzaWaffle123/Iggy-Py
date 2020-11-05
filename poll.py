import discord

tracked_polls = {} # dict of form Message:Poll()

poll_open = discord.Colour.from_rgb(126, 211, 33)
poll_closed = discord.Colour.from_rgb(214, 40, 61)
poll_notready = discord.Colour.from_rgb(150, 150, 150)


class Poll:
    def __init__(self, question, options):
        self.question = question

        self.emoji_map = {} # maps reaction emojis to options
        self.vote_counter = {} # counts how many votes have been recorded for each emoji

        self.options = options
        starting_char = 97
        for opt in self.options:
            char = chr(starting_char)
            emoji_code = "regional_indicator_" + char

        self.poll_embed = discord.Embed()

        self.poll_embed.title = self.question



