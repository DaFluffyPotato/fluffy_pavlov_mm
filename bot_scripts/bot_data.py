import discord

from .queue import Queues
from .config import config

class BotData:
    def __init__(self):
        self.guild = None
        self.matches_category = None
        self.next_match_id = 0
        self.active_matches = []

    def load(self, guild):
        self.guild = guild

        self.queues = Queues(self)
        for queue_id in config['queues']:
            queue = config['queues'][queue_id]
            self.queues.new_queue(queue_id, discord.utils.get(guild.channels, name=queue['channel']).id, queue['player_count'])
            self.queues.new_queue(queue_id, discord.utils.get(guild.channels, name=queue['channel']).id, queue['player_count'])

        self.matches_category = discord.utils.get(guild.categories, name='matches')

bot_data = BotData()
