import time

from .config import config
from .vote import Vote
from .util import grammatical_list, emoji_list

class Match:
    def __init__(self, bot_data, queue_id, teams, mmr_diff=0):
        self.queue_id = queue_id
        self.bot_data = bot_data
        self.match_id = bot_data.next_match_id
        bot_data.next_match_id += 1
        self.teams = teams
        self.mmr_diff = mmr_diff
        self.waiting_to_gen = True
        self.team_roles = []
        self.team_sides = [None, None]
        self.owned_channels = []

        self.team_ready_counts = [0 for team in teams]

        self.map_set = bot_data.get_maps(queue_id)
        self.selected_map = None

        self.state = 0
        self.state_start = time.time()
        self.current_vote = None

    def next_state(self):
        self.state += 1
        self.state_start = time.time()

    async def full_init(self):
        self.waiting_to_gen = False
        await self.create_roles()
        await self.create_channels()

    @property
    def match_info_msg(self):
        output = '**Match ' + str(self.match_id) + ' (' + self.queue_id + ')**\n'
        output += 'Map: **' + str(self.selected_map) + '**\n\n'
        output += 'Team A (**' + str(self.team_sides[0]) + '**): ' + grammatical_list([user.name for user in self.teams[0]]) + '\n'
        output += 'Team B (**' + str(self.team_sides[1]) + '**): ' + grammatical_list([user.name for user in self.teams[1]]) + '\n\n'
        output += '*A player from each team needs to submit their own team\'s score after the match ends. For example, if the final score is 10-7 with Team A winning, a player from Team A should do `!submitscore 10` and a player from Team B should do `!submitscore 7`.*'
        return output

    async def tick(self):
        time_passed = time.time() - self.state_start

        if self.current_vote:
            self.current_vote.tick()

        if self.state == 1:
            self.next_state()
            vote_msg = await self.team_a_channels[0].send('Please select 3 maps to ban.\n' + emoji_list(self.map_set))
            await self.team_b_channels[0].send('Team A is voting on bans.')
            self.current_vote = Vote(vote_msg, len(self.map_set), max_choices=3, duration=config['vote_durations'])
            await self.current_vote.finish_init()

        if (self.state == 2) and (self.current_vote):
            if self.current_vote.result:
                vote_results = sorted(self.current_vote.result, key=lambda x: x[1], reverse=True)[:3]
                self.next_state()
                self.current_vote.result = None
                bans = [self.map_set[vote[0] - 1] for vote in vote_results]
                await self.team_a_channels[0].send('Banned ' + grammatical_list(bans) + '.')
                await self.team_b_channels[0].send('Team A banned ' + grammatical_list(bans) + '.')
                for ban in bans:
                    self.map_set.remove(ban)

                vote_msg = await self.team_b_channels[0].send('Please select a map to play.\n' + emoji_list(self.map_set))
                await self.team_a_channels[0].send('Team B is voting on the map.')
                self.current_vote = Vote(vote_msg, len(self.map_set), max_choices=1, duration=config['vote_durations'])
                await self.current_vote.finish_init()

        if (self.state == 3) and (self.current_vote):
            if self.current_vote.result:
                vote_results = sorted(self.current_vote.result, key=lambda x: x[1], reverse=True)[0]
                self.next_state()
                self.current_vote.result = None
                self.selected_map = self.map_set[vote_results[0] - 1]
                await self.team_a_channels[0].send(self.selected_map + ' was chosen as the map for the match.')
                await self.team_b_channels[0].send(self.selected_map + ' was chosen as the map for the match.')

                vote_msg = await self.team_a_channels[0].send('Please choose a side.\n' + emoji_list(['T', 'CT']))
                await self.team_b_channels[0].send('Team A is choosing sides.')
                self.current_vote = Vote(vote_msg, 2, max_choices=1, duration=config['vote_durations'])
                await self.current_vote.finish_init()

        if (self.state == 4) and (self.current_vote):
            if self.current_vote.result:
                vote_results = sorted(self.current_vote.result, key=lambda x: x[1], reverse=True)[0]
                self.next_state()
                self.current_vote.result = None
                if vote_results[0] == 1:
                    self.team_sides = ['T', 'CT']
                else:
                    self.team_sides = ['CT', 'T']

                await self.team_a_channels[0].delete()
                await self.team_b_channels[0].delete()
                new_channel = await self.bot_data.guild.create_text_channel('match-' + str(self.match_id), category=self.bot_data.matches_category)
                for role in self.team_roles:
                    new_channel.set_permissions(self.team_roles[0], send_messages=True, read_messages=True)
                self.team_a_channels[0] = new_channel
                self.team_b_channels[0] = new_channel
                self.owned_channels.append(new_channel)

                await new_channel.send(self.match_info_msg)

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
                    self.next_state()

            if self.current_vote:
                self.current_vote.process_reaction(reaction, user)
