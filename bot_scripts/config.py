config = {
    'match_category': 'matches',
    'admin_commands_channel': 'admin-commands',
    'match_results_channel': 'match-results',
    'vote_durations': 10,
    'score_acceptance_duration': 10,
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
