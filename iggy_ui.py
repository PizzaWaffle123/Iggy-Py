from discord import ui, Interaction, ButtonStyle
from random import shuffle
import database
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
        print("-------------------")
        print(str(interaction.data))

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

        self.placeholder="Select a Group"
        self.add_option(
            label="Current Student",
            description="I currently attend Holy Cross and have a Holy Cross email.",
            value="student",
            emoji="📘"
        )
        self.add_option(
            label="Incoming Student",
            description="I will attend Holy Cross, but I don't have an email yet.",
            value="incoming",
            emoji="🎒"
        )
        self.add_option(
            label="Prospective Student",
            description="I am interested in attending/applying to Holy Cross.",
            value="prospect",
            emoji="📑"
        )
        self.add_option(
            label="Former Student",
            description="I previously attended/graduated from Holy Cross.",
            value="alumni",
            emoji="🎓"
        )
        self.add_option(
            label="Guest",
            description="I do not attend Holy Cross.",
            value="guest",
            emoji="🎟"
        )


class ManageTeamsDropdown(ui.Select):

    async def callback(self, interaction: Interaction):
        val = interaction.data["values"][0] # dropdown selection
        user_id = interaction.data['custom_id']
        view = None
        if val == 'new':
            team_data = database.get_teams(user_id=user_id, invert=True)
            content = f"Managing esports for <@{user_id}>."
            view = ui.View.from_message(interaction.message).clear_items()
            view.add_item(AddNewTeamDropdown(user_id=user_id, items=team_data))
        else:
            team_data = database.get_teams(identifier=val)[0]
            curr_position = database.get_positions(user_id=user_id, team_id=val)[0][0]
            new_positions = database.get_positions(user_id=user_id, team_id=val, invert=True)
            content = f"Managing esports for <@{user_id}> on **{team_data[0]}**."
            view = ui.View.from_message(interaction.message).clear_items()
            view.add_item(EditPositionDropdown(user_id=user_id, team_id= val, default_text=curr_position, items=new_positions))
        await interaction.response.edit_message(
                content=content,
                view=view
             )

    def __init__(self, default_text="Select a Team to Manage", items=[], user_id=None):
        super().__init__()
        if not user_id : return
        self.placeholder=default_text
        self.custom_id=str(user_id)
        for item in items:
            self.add_option(
                label=item[0],
                value=item[1],
                emoji=item[2]
            )


class AddNewTeamDropdown(ui.Select):
    # this callback follows the selection of a new team to add a user to
    async def callback(self, interaction: Interaction):
        val = interaction.data["values"][0] # dropdown selection
        user_id = interaction.data['custom_id']
        view = None
        team_data = database.get_teams(identifier=val)[0]
        new_positions = database.get_positions()
        view = ui.View.from_message(interaction.message).clear_items()
        view.add_item(EditPositionDropdown(user_id=user_id, team_id= val, items=new_positions))
        await interaction.response.edit_message(
                content=f"Managing esports for <@{user_id}> on **{team_data[0]}**.",
                view=view
             )

    def __init__(self, default_text="Select a Team to Add", items=[], user_id=None):
        super().__init__()
        if not user_id : return
        self.placeholder=str(default_text)
        self.custom_id=user_id
        for item in items:
            self.add_option(
                label=item[0],
                value=item[1],
                emoji=item[2]
            )


class EditPositionDropdown(ui.Select):

    async def callback(self, interaction: Interaction):
        id_list = list(interaction.data['custom_id'].split(" "))
        user_id = id_list[0]
        team_id = id_list[1]
        position_id = interaction.data["values"][0] # dropdown selection
        if position_id == 'remove':
            database.manage_player(user_id=user_id, team_id=team_id)
        else:
            database.manage_player(user_id=user_id, team_id=team_id, position_id=position_id)
        team = database.get_team_from_id(team_id)
        position = database.get_position_from_id(position_id)
        new_positions = database.get_positions(user_id=user_id, team_id=team_id, position_id=position_id, invert=True)
        content = f"Managing esports for <@{user_id}> on **{team}**.\n<@{user_id}> successfully assigned to **{position}** on **{team}**."
        if not position : content = f"Managing esports for <@{user_id}> on **{team}**.\n<@{user_id}> successfully **removed** from **{team}**."
        view = ui.View.from_message(interaction.message).clear_items()
        view.add_item(EditPositionDropdown(user_id=user_id, team_id=team_id, default_text=position, items=new_positions))
        await interaction.response.edit_message(
            view=view,
            content=content
        )

    # self, user being managed, team being managed, list of positions to display, optional placeholder text
    def __init__(self, user_id=None, team_id=None, items=[], default_text=None):
        super().__init__()
        if not user_id : return
        for item in items:
            self.add_option(
                label=item[0],
                value=item[1],
                emoji=item[2]
            )
        # if a current position is provided as default text, display Current Position
        # and provide the option to remove the player from the currently selected team
        if default_text:
            self.placeholder="Current Position: " + str(default_text)
            self.add_option(label="Remove from Team", value="remove", emoji="❌")
        else:
            self.placeholder="Select a Position"
        self.custom_id=' '.join(map(str, [user_id, team_id]))



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
