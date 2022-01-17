config = {
    'match_category': 'matches',
    'admin_commands_channel': 'admin-commands',
    'match_results_channel': 'match-results',
    'vote_durations': 10,
    'score_acceptance_duration': 10,
    'base_mmr': 1000,
    'database_uri': 'mongodb://dafluffypotato:<password>@dafluffypotato-db-shard-00-00-b1wgg.mongodb.net:27017,dafluffypotato-db-shard-00-01-b1wgg.mongodb.net:27017,dafluffypotato-db-shard-00-02-b1wgg.mongodb.net:27017/test?ssl=true&replicaSet=DaFluffyPotato-DB-shard-0&authSource=admin&retryWrites=true&w=majority',
    'queues': {
        '5v5': {
            'player_count': 10,
            'channel': '5v5-queue',
            'maps': ['Sand', 'Museum', 'Stockpile', 'Oilrig', 'Cache', 'Mirage', 'Dust 2', 'Seaside', 'Stahlbrecher', 'Reachsky', 'Overpass', 'Manor'],
        },
        '3v3': {
            'player_count': 2,
            'channel': '3v3-queue',
            'maps': ['Sand', 'Mirage', 'Museum', 'Reachsky', 'Cache', 'Stockpile'],
        },
    }
}
