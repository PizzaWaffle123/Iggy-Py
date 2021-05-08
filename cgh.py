import discord


class CGH:
    def __init__(self, guild):
        # All of those long numbers are role or channel IDs.
        # Information on obtaining them is in README.txt
        self.guild = guild
        self.role_pending = guild.get_role(682283357257990236)
        self.role_crusader = guild.get_role(432940984452513795)
        self.role_eboard = guild.get_role(681213070592573481)
        self.role_guest = guild.get_role(702380501188739163)
        self.role_bullhorn = guild.get_role(839899985143398480)
        self.channel_general = guild.get_channel(441445458897010717)
        self.channel_member_log = guild.get_channel(682342799940649014)
        self.guest_requests = {}

    def count_members(self):
        # Returns a count of the members in the server who have specific roles.
        # In CGH, we use this to only count Crusaders and E-Board members. Guests and Pending users do not get counted.
        count = 0
        for member in self.guild.members:
            for role in member.roles:
                if role in [self.role_crusader, self.role_eboard]:
                    count += 1
                    break
        return count

    async def new_user(self, user):
        # Simply adds the Pending role to the user provided as a parameter.
        member = self.guild.get_member(user_id=user.id)
        if member is None:
            return
        await member.add_roles(self.role_pending)

    async def verify_user(self, user, user_email):
        # This function gets called when a user has completed verification.
        # It is used for role adjustment and logging.
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

    async def verify_user_prospective(self, user):
        member = self.guild.get_member(user_id=user.id)
        if member is None:
            return
        if self.role_pending in member.roles:
            await member.remove_roles(self.role_pending)
        await member.add_roles(self.role_crusader)
        logged_user = discord.Embed()
        logged_user.title = "New Prospective User"
        logged_user.add_field(name="Username", value="%s#%s" % (user.name, user.discriminator), inline=False)
        logged_user.add_field(name="Year of Graduation", value="2025", inline=False)
        logged_user.set_thumbnail(url=user.avatar_url)
        logged_user.colour = discord.Colour.from_rgb(66, 221, 245)
        await self.channel_member_log.send(embed=logged_user)

    async def username_update(self, u_before, u_after):
        # Handles logging of users changing their username.
        old_username = "%s#%s" % (u_before.name, u_before.discriminator)
        new_username = "%s#%s" % (u_after.name, u_after.discriminator)
        username_change = discord.Embed()
        username_change.title = "User Changed Name"
        username_change.colour = discord.Colour.from_rgb(245, 166, 35)
        username_change.description = "Don't forget to update the Discord roster!"
        username_change.add_field(name="Previous", value=old_username, inline=True)
        username_change.add_field(name="Current", value=new_username, inline=True)
        await self.channel_member_log.send(embed=username_change)

    async def notify_of_guest(self, user):
        # Creates dynamic Guest Pass embed usable by moderators.
        guest_request = discord.Embed()
        guest_request.title = "Guest Pass Requested"
        guest_request.set_thumbnail(url=user.avatar_url)
        guest_request.description = "\U0001f7e9 Approve\n" \
                                    "\U0001f7e5 Deny"
        guest_request.add_field(name="Username", value="%s#%s" % (user.name, user.discriminator), inline=False)
        guest_request.colour = discord.Colour.from_rgb(150, 150, 150)
        sent_message = await self.channel_member_log.send(embed=guest_request)
        await sent_message.add_reaction("\U0001f7e9")  # green square
        await sent_message.add_reaction("\U0001f7e5")  # red square
        self.guest_requests[sent_message] = user

    async def verify_guest(self, message):
        # Used to "approve" a Guest Pass.
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
        # Used for logging users who leave the server.
        # Only logs departures of Crusaders and E-Board.
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

    async def bullhorn_send(self, message):
        bullhorn_list = []
        for member in self.guild.members:
            # Step 1: Identify all users opted in to Bullhorn.
            bullhorn_mem = False
            for role in member.roles:
                if role == self.role_bullhorn:
                    bullhorn_mem = True
                    break
            if bullhorn_mem:
                bullhorn_list.append(member)

        for bh_member in bullhorn_list:
            # Step 2: Send the message to all users opted in to Bullhorn.
            if bh_member.dm_channel is None:
                await bh_member.create_dm()
            try:
                print("Sending bullhorn to user: " + bh_member.name)
                await bh_member.dm_channel.send("Incoming Bullhorn from the Crusader Gaming Hub!")
                await bh_member.dm_channel.send(content=message.content)
            except discord.errors.Forbidden:
                print("UNABLE TO SEND BULLHORN - USER MAY HAVE DMs BLOCKED")









