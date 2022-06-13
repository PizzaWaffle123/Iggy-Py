from discord import ui, Interaction, TextStyle


class DatabaseEditModal(ui.Modal):
    name = ui.TextInput(
        custom_id="name",
        label="User's Full Name",
        style=TextStyle.short,
        required=True,
        max_length=24
    )

    grad_year = ui.TextInput(
        custom_id="gradyear",
        label="User's Grad Year",
        style=TextStyle.short,
        required=True,
        max_length=4
    )

    email_address = ui.TextInput(
        custom_id="email",
        label="User's Holy Cross Email",
        style=TextStyle.short,
        required=True,
        max_length=24
    )

    def __init__(self, data):
        super().__init__(
            title="Modify Database Information"
        )
        self.name.default = data[1]
        self.grad_year.default = data[2]
        self.email_address.default = data[3]


    async def on_submit(self, interaction: Interaction):
        await interaction.response.send_message(
            ephemeral=True,
            content="Submitted."
        )
