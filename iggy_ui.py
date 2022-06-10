from discord import ui, Interaction, ButtonStyle
from random import shuffle

import verify


class MenuVerify(ui.View):

    def __init__(self):
        super().__init__()

        self.add_item(GroupDropdown())


class SecurityCode(ui.View):

    def __init__(self, codelist):
        super().__init__()
        shuffle(codelist)
        for code in codelist:
            self.add_item(CodeButton(code))


class GroupDropdown(ui.Select):

    async def callback(self, interaction: Interaction):
        val = interaction.data["values"][0]

        if val == "student":
            await interaction.response.send_modal(
                verify.StudentEmailModal()
            )
        else:
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


class CodeButton(ui.Button):

    def __init__(self, code):
        super().__init__()
        self.label = str(code)
        self.custom_id = str(code)
        self.style = ButtonStyle.blurple

    async def callback(self, interaction: Interaction):
        result = verify.check_code(interaction)
        if result:
            await interaction.response.send_modal(
                verify.StudentIntroModal()
            )
        else:
            await interaction.response.edit_message(
                view=None,
                content="You picked the wrong code!\nPlease attempt to verify again!"
            )
