import random

import discord

from .util import read_f
from .queue import Queues
from .config import config
from .database import Database

class BotData:
    def __init__(self):
        self.guild = None
        self.matches_category = None
        self.emotes = {}
        self.next_match_id = 0
        self.active_matches = []
        self.db = Database(read_f('dbpass.txt').replace('\n', ''))
        self.rank_roles = {}

    def get_maps(self, queue_id, count=6):
        map_set = config['queues'][queue_id]['maps']
        random.shuffle(map_set)
        return map_set[:count]

    def load(self, guild):
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
