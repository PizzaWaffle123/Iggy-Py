from discord import ui, Interaction


class MenuVerify(ui.View):

    def __init__(self):
        super().__init__()

        self.add_item(GroupDropdown())


class GroupDropdown(ui.Select):

    async def callback(self, interaction: Interaction):
        val = interaction.data["values"][0]

        await interaction.response.send_message(
            ephemeral=True,
            content=f"You chose: {val}\nThanks for your response!"
        )

    def __init__(self):
        super().__init__()

        self.add_option(
            label="Current Student",
            description="I currently attend Holy Cross, and have a Holy Cross email.",
            value="student"
        )
        self.add_option(
            label="Incoming Student",
            description="I will be attending Holy Cross (no email yet).",
            value="incoming"
        )

        self.add_option(
            label="Prospective Student",
            description="I am interested in attending Holy Cross.",
            value="prospect"
        )
        self.add_option(
            label="Former Student",
            description="I previously attended/graduated from Holy Cross.",
            value="alumni"
        )
        self.add_option(
            label="Guest",
            description="I do not attend Holy Cross.",
            value="guest"
        )
