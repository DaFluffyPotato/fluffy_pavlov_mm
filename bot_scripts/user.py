from .config import config

class User:
    def __init__(self, bot_data, discord_user):
        self.bot_data = bot_data
        self.id = discord_user.id
        self.name = discord_user.display_name
        self.discord_user = discord_user
        self.queue_stats = {}
        self.ban_until = 0

        self.refresh()

    def refresh(self):
        json_data = self.bot_data.db.get_user(self.discord_user)

        self.queue_stats = json_data['queue_stats']
        self.ban_until = json_data['ban_until']

    def save(self):
        self.bot_data.db.save_user(self)

    def get_mmr(self, queue_id):
        if queue_id not in self.queue_stats:
            self.queue_stats[queue_id] = {'mmr': config['base_mmr']}
        return self.queue_stats[queue_id]['mmr']
