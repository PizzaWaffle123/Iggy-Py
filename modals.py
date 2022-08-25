from discord import ui, Interaction, TextStyle

import database
import verify


class DatabaseEditModal(ui.Modal):
    target = None
    name = ui.TextInput(
        custom_id="name",
        label="Full Name",
        style=TextStyle.short,
        required=True,
        max_length=24
    )

    grad_year = ui.TextInput(
        custom_id="grad_year",
        label="Grad Year",
        style=TextStyle.short,
        required=True,
        max_length=4
    )

    email_address = ui.TextInput(
        custom_id="email",
        label="Holy Cross Email Address",
        style=TextStyle.short,
        required=True,
        max_length=24
    )

    def __init__(self, data, target_user):
        super().__init__(
            title="Modify Database Information"
        )
        self.name.default = data[1]
        self.grad_year.default = data[2]
        self.email_address.default = data[3]

        self.target = target_user

    async def on_submit(self, interaction: Interaction):
        # print(interaction.data['components'])
        print(self.target)
        data_to_set = {}
        # Step 1 - Parse out the needed data.
        for com in interaction.data['components']:
            modal_input = com['components'][0]
            data_to_set[modal_input['custom_id']] = modal_input['value']

        # Step 2 - Input validation.
        if not verify.email_is_valid(data_to_set['email']):
            await interaction.response.send_message(
                ephemeral = True,
                content="ERROR: Invalid email address provided!\n*No changes were made.*"
            )
            return

        if not data_to_set['grad_year'].isnumeric():
            await interaction.response.send_message(
                ephemeral=True,
                content="ERROR: Invalid graduation year provided!\n*No changes were made.*"
            )
            return

        # Step 3 - Construct the appropriate query.
        print(data_to_set)
        query = "UPDATE users SET "
        for k in data_to_set.keys():
            stub = f"{k}=\"{data_to_set[k]}\", "
            query += stub
        query = query[:-2]
        query += f" WHERE user_id={self.target.id}"
        print(query)
        database.raw_query(query)
        await interaction.response.send_message(
            ephemeral=True,
            content="Changes submitted."
        )
