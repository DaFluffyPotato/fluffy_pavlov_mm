config = {
    'ranks': [
        ['Diamond', 1850],
        ['Platinum', 1725],
        ['Gold', 1600],
        ['Silver', 1450],
        ['Bronze', 1375],
        ['Iron', -99999],
    ],
    'match_category': 'matches',
    'admin_commands_channel': 'admin-commands',
    'match_results_channel': 'match-results',
    'vote_durations': 30,
    'score_acceptance_duration': 10,
    'base_mmr': 1500,
    'duo_limit': 1600,
    'ping_cooldown': 60,
    'database_uri': 'mongodb://dafluffypotato:<password>@dafluffypotato-db-shard-00-00-b1wgg.mongodb.net:27017,dafluffypotato-db-shard-00-01-b1wgg.mongodb.net:27017,dafluffypotato-db-shard-00-02-b1wgg.mongodb.net:27017/test?ssl=true&replicaSet=DaFluffyPotato-DB-shard-0&authSource=admin&retryWrites=true&w=majority',
    'queues': {
        '5v5': {
            'player_count': 10,
            'channel': '5v5-queue',
            'maps': ['Sand', 'Museum', 'Stockpile', 'Oilrig', 'Cache', 'Mirage', 'Dust 2', 'Seaside', 'Stahlbrecher', 'Reachsky', 'Overpass', 'Manor'],
        },
        '2v2': {
            'player_count': 4,
            'channel': '2v2-queue',
            'maps': ['Museum', 'Reachsky', 'Stockpile', 'Business', 'Chess 2', 'Gravity', 'Rialto', 'Nuketown', 'Baggage'],
        },
    }
}
