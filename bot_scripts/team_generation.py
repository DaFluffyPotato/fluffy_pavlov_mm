from itertools import permutations

def generate_teams(users, queue_id):
    best_teams = [None, 99999999]
    for permutation in permutations(users):
        team_1 = permutation[:len(permutation) // 2]
        team_2 = permutation[len(permutation) // 2:]
        team_1_mmr = sum([user.get_mmr(queue_id) for user in team_1])
        team_2_mmr = sum([user.get_mmr(queue_id) for user in team_2])
        mmr_diff = abs(team_1_mmr - team_2_mmr)
        if mmr_diff < best_teams[1]:
            best_teams = [[team_1, team_2], mmr_diff]
    return best_teams
