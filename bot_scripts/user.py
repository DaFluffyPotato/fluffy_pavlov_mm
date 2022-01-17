from .config import config

class User:
    def __init__(self, discord_user):
        self.id = discord_user.id
        self.name = discord_user.display_name
        self.discord_user = discord_user
        self.queue_stats = {queue: {'mmr': 1000} for queue in config['queues']}
