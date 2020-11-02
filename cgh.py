import discord


class CGH:
    def __init__(self, guild):
        self.guild = guild
        self.role_pending = guild.get_role(682283357257990236)
        self.role_crusader = guild.get_role(432940984452513795)
        self.role_eboard = guild.get_role(681213070592573481)
        self.role_guest = guild.get_role(702380501188739163)
        self.channel_general = guild.get_channel(441445458897010717)
        self.channel_member_log = guild.get_channel(682342799940649014)

    def count_members(self):
        count = 0
        for member in self.guild.members:
            for role in member.roles:
                if role in [self.role_crusader, self.role_eboard]:
                    count += 1
                    break

        return count

    async def new_user(self, user):
        member = self.guild.get_member(user_id=user.id)
        if member is None:
            return
        await member.add_roles(self.role_pending)

    async def verify_user(self, user, user_email):
        member = self.guild.get_member(user_id=user.id)
        if member is None:
            return
        if self.role_pending in member.roles:
            await member.remove_roles(self.role_pending)
        await member.add_roles(self.role_crusader)
        logged_user = discord.Embed()
        logged_user.title = "New Verified User"
        logged_user.add_field(name="Username", value="%s#%s" % (user.name, user.discriminator), inline=False)
        logged_user.add_field(name="Email Address", value=user_email, inline=False)
        logged_user.set_thumbnail(url=user.avatar_url)
        logged_user.colour = discord.Colour.from_rgb(126, 211, 33)
        await self.channel_member_log.send(embed=logged_user)

    async def username_update(self, u_before, u_after):
        old_username = "%s#%s" % (u_before.name, u_before.discriminator)
        new_username = "%s#%s" % (u_after.name, u_after.discriminator)
        username_change = discord.Embed()
        username_change.title = "User Changed Name"
        username_change.colour = discord.Colour.from_rgb(245, 166, 35)
        username_change.add_field(name="Previous", value=old_username, inline=True)
        username_change.add_field(name="Current", value=new_username, inline=True)
        username_change.description = "Make sure to update the verified user sheet immediately!"
        await self.channel_member_log.send(embed=username_change)

