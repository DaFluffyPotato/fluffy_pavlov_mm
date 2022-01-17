import pymongo

from .config import config

class Database:
    def __init__(self, password):
        connect_uri = config['database_uri'].replace('<password>', password)
        self.db_client = pymongo.MongoClient(connect_uri, connectTimeoutMS=30000, socketTimeoutMS=None, socketKeepAlive=True, connect=False, maxPoolsize=1)
        self.db = self.db_client['fluffy_pavlov_mm']

    def save_match(self, match):
        match_data = {
            'match_id': match.match_id,
            'queue_id': match.queue_id,
            'map': match.selected_map,
            'scores': match.scores,
            'all_users': [user.id for user in match.teams[0] + match.teams[1]],
            'teams': [[user.id for user in match.teams[0]], [user.id for user in match.teams[0]]],
            'creation_date': match.creation_date,
            'end_date': match.end_date,
            'mmr_diff': match.mmr_diff,
            'winner': match.winner,
        }

        self.db['matches'].insert_one(match_data)

    def create_user(self, discord_user):
        user_data = {
            '_id': discord_user.id,
            'queue_stats': {},
            'name': discord_user.display_name,
            'ban_until': 0,
        }

        self.db['users'].insert_one(user_data)

        return user_data

    def save_user(self, user):
        self.db['users'].update_one({'_id': user.id}, {'$set': {
            'name': user.name,
            'queue_stats': user.queue_stats,
            'ban_until': user.ban_until,
        }})

    def get_users(self, discord_users):
        user_ids = {user.id: user for user in discord_users}
        users_found = list(self.db['users'].find({'_id': {'$in': list(user_ids)}}))
        user_ids_found = [user['_id'] for user in users_found]
        for user in user_ids:
            if user not in user_ids_found:
                users_found.append(self.create_user(user_ids[user]))
        return users_found

    def get_user(self, discord_user):
        user = self.db['users'].find_one({'_id': discord_user.id})
        if not user:
            user = self.create_user(discord_user)
        return user
