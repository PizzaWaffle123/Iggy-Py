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
        self.guest_requests = {}

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
        username_change.description = "Make sure to update the verified user sheet immediately!"
        username_change.add_field(name="Previous", value=old_username, inline=True)
        username_change.add_field(name="Current", value=new_username, inline=True)
        await self.channel_member_log.send(embed=username_change)

    async def notify_of_guest(self, user):
        guest_request = discord.Embed()
        guest_request.title = "User Requesting Guest Pass"
        guest_request.set_thumbnail(url=user.avatar_url)
        guest_request.description = "React with either a green or red square to approve/deny the request."
        guest_request.add_field(name="Username", value="%s#%s" % (user.name, user.discriminator), inline=False)
        guest_request.colour = discord.Colour.from_rgb(150, 150, 150)
        sent_message = await self.channel_member_log.send(embed=guest_request)
        await sent_message.add_reaction("\U0001f7e9")  # green square
        await sent_message.add_reaction("\U0001f7e5")  # red square
        self.guest_requests[sent_message] = user

    async def verify_guest(self, message):
        if message not in self.guest_requests.keys():
            return
        user = self.guest_requests[message]
        member = self.guild.get_member(user_id=user.id)
        if member is None:
            return
        if self.role_pending in member.roles:
            await member.remove_roles(self.role_pending)
        await member.add_roles(self.role_guest)

    async def user_left(self, member):
        valid = False

        for role in member.roles:
            if role in [self.role_crusader, self.role_eboard]:
                valid = True
                break

        if valid is False:
            return

        departure_notice = discord.Embed()
        departure_notice.title = "User Left Server"
        departure_notice.add_field(name="Remaining Members", value="➤ %d" % self.count_members(), inline=False)
        departure_notice.colour = discord.Colour.from_rgb(214, 40, 61)
        departure_notice.set_author(name="%s#%s" % (member.name, member.discriminator), url=None,
                                    icon_url=member.avatar_url)
        await self.channel_member_log.send(embed=departure_notice)





