from .match import Match
from .util import grammatical_list
from .team_generation import generate_teams

class Queues:
    def __init__(self, bot_data):
        self.bot_data = bot_data
        self.queues = {}
        self.debug_mode = False

    @property
    def all_users(self):
        users = []
        for queue in self.queues.values():
            users += queue.users
        return users

    @property
    def all_user_ids(self):
        return [user.id for user in self.all_users]

    def find_channel_queue(self, channel_id):
        for queue in self.queues.values():
            if queue.channel_id == channel_id:
                return queue.id
        return None

    def new_queue(self, queue_id, channel_id, player_count):
        self.queues[queue_id] = Queue(self.bot_data, queue_id, channel_id, player_count)

    def join_queue(self, user, queue_id):
        if (user.id not in self.all_user_ids) or (self.debug_mode):
            self.queues[queue_id].add_user(user)
            return True
        return False

    def leave_queue(self, user, queue_id):
        if user.id in self.all_user_ids:
            self.queues[queue_id].remove_user(user)
            return True
        return False

class Queue:
    def __init__(self, bot_data, custom_id, channel_id, match_player_count):
        self.bot_data = bot_data
        self.id = custom_id
        self.channel_id = channel_id
        self.match_player_count = match_player_count
        self.users = []
        self.creating_match = False

    @property
    def player_count(self):
        return len(self.users)

    def create_match(self):
        # lock queue
        self.creating_match = True

        while len(self.users) >= self.match_player_count:
            teams, mmr_diff = generate_teams(self.users[:10], self.id)
            for team in teams:
                for user in team:
                    self.users.remove(user)
            self.bot_data.active_matches.append(Match(self.bot_data, self.id, teams, mmr_diff=mmr_diff))

        # unlock queue
        self.creating_match = False

    def add_user(self, user):
        self.users.append(user)
        if len(self.users) >= self.match_player_count:
            if not self.creating_match:
                self.create_match()

    def remove_user(self, user):
        for user_in_queue in self.users:
            if user_in_queue.id == user.id:
                self.users.remove(user_in_queue)
                return True
        return False

    @property
    def user_list_str(self):
        return grammatical_list([user.name for user in self.users])
