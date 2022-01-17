from .util import grammatical_list

class Match:
    def __init__(self, bot_data, teams, mmr_diff=0):
        self.bot_data = bot_data
        self.match_id = bot_data.next_match_id
        bot_data.next_match_id += 1
        self.teams = teams
        self.mmr_diff = mmr_diff
        self.waiting_to_gen = True
        self.team_roles = []
        self.owned_channels = []

        self.team_ready_counts = [0 for team in teams]

    async def full_init(self):
        self.waiting_to_gen = False
        await self.create_roles()
        await self.create_channels()

    async def create_roles(self):
        team_a_role = await self.bot_data.guild.create_role(name='match-' + str(self.match_id) + '-a')
        team_b_role = await self.bot_data.guild.create_role(name='match-' + str(self.match_id) + '-b')

        self.team_roles.append(team_a_role)
        self.team_roles.append(team_b_role)

        for user in self.teams[0]:
            await user.discord_user.add_roles(team_a_role)

        for user in self.teams[1]:
            await user.discord_user.add_roles(team_b_role)

    async def create_channels(self):
        self.team_a_channels = []
        self.team_b_channels = []
        team_a_channels = self.team_a_channels
        team_b_channels = self.team_b_channels
        team_a_channels.append(await self.bot_data.guild.create_text_channel('match-' + str(self.match_id) + '-a', category=self.bot_data.matches_category))
        team_b_channels.append(await self.bot_data.guild.create_text_channel('match-' + str(self.match_id) + '-b', category=self.bot_data.matches_category))
        team_a_channels.append(await self.bot_data.guild.create_voice_channel('match-' + str(self.match_id) + '-a', category=self.bot_data.matches_category))
        team_b_channels.append(await self.bot_data.guild.create_voice_channel('match-' + str(self.match_id) + '-b', category=self.bot_data.matches_category))

        for channel in team_a_channels + team_b_channels:
            self.owned_channels.append(channel)

        for i, channel in enumerate(team_a_channels):
            if i != 1:
                await channel.set_permissions(self.team_roles[0], send_messages=True, read_messages=True)
            else:
                await channel.set_permissions(self.team_roles[0], connect=True)

        for i, channel in enumerate(team_b_channels):
            if i != 1:
                await channel.set_permissions(self.team_roles[1], send_messages=True, read_messages=True)
            else:
                await channel.set_permissions(self.team_roles[1], connect=True)

        team_a_mentions = grammatical_list([user.discord_user.mention for user in self.teams[0]])
        team_b_mentions = grammatical_list([user.discord_user.mention for user in self.teams[1]])

        general_first_msg_text = '\n\nReact with a check mark below to mark yourself as ready within the next 5 minutes.'

        self.team_a_init_msg = await team_a_channels[0].send('Your team (A): ' + team_a_mentions + '\nEnemy team (B): ' + team_b_mentions + general_first_msg_text)
        self.team_b_init_msg = await team_b_channels[0].send('Your team (B): ' + team_b_mentions + '\nEnemy team (A): ' + team_a_mentions + general_first_msg_text)

        await self.team_a_init_msg.add_reaction('✅')
        await self.team_b_init_msg.add_reaction('✅')

    async def process_reaction(self, reaction, user):
        if reaction.message.channel in self.owned_channels:
            ready_reaction = False
            if self.team_a_init_msg == reaction.message:
                self.team_ready_counts[0] += 1
                ready_reaction = True
            if self.team_b_init_msg == reaction.message:
                self.team_ready_counts[1] += 1
                ready_reaction = True

            if ready_reaction:
                if sum(self.team_ready_counts) >= len(self.teams[0] * len(self.teams)) + len(self.teams):
                    await self.team_a_channels[0].send('Both teams have accepted the match. Map voting will now begin.')
                    await self.team_b_channels[0].send('Both teams have accepted the match. Map voting will now begin.')
