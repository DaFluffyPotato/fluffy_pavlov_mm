import random

import discord

from .util import read_f
from .queue import Queues
from .config import config
from .database import Database

class BotData:
    def __init__(self):
        self.client = None
        self.guild = None
        self.matches_category = None
        self.emotes = {}
        self.active_matches = []
        self.db = Database(read_f('dbpass.txt').replace('\n', ''))
        self.refresh_ping_rules()
        self.rank_roles = {}
        self.queues = None
        self.duo_invites = []

    def refresh_ping_rules(self):
        self.ping_rules = self.db.get_ping_rules()

    def get_users_in_matches(self):
        user_ids = []
        for match in self.active_matches:
            user_ids += match.all_user_ids
        return user_ids

    def get_match_id(self):
        self.db.db['counters'].update_one({'_id': 'match_id'}, {'$inc': {'count': 1}}, upsert=True)
        new_id = self.db.db['counters'].find_one({'_id': 'match_id'})['count']
        return new_id

    def get_match(self, match_id):
        for match in self.active_matches:
            if match.match_id == match_id:
                return match

    def get_maps(self, queue_id, count=6):
        map_set = config['queues'][queue_id]['maps']
        random.shuffle(map_set)
        return map_set[:count]

    def load(self, client, guild):
        self.client = client
        self.guild = guild

        self.queues = Queues(self)
        for queue_id in config['queues']:
            queue = config['queues'][queue_id]
            self.queues.new_queue(queue_id, discord.utils.get(guild.channels, name=queue['channel']).id, queue['player_count'])
            self.queues.new_queue(queue_id, discord.utils.get(guild.channels, name=queue['channel']).id, queue['player_count'])

        self.matches_category = discord.utils.get(guild.categories, name='matches')

        for emoji in guild.emojis:
            self.emotes[emoji.name] = ('<:' + emoji.name + ':' + str(emoji.id) + '>', emoji)

        for rank in config['ranks']:
            role = discord.utils.get(guild.roles, name=rank[0].lower())
            if role:
                self.rank_roles[rank[0]] = role

bot_data = BotData()
