import random

from itertools import permutations

def generate_teams(users, queue_id, duos):
    best_teams = [None, 99999999]
    team_arrangements = list(permutations(users))
    random.shuffle(team_arrangements)

    # clear out invalid duos due to a player not being in queue
    all_users = [user.id for user in users]
    for duo in duos[::-1]:
        if len(set(all_users) - set(duo)) != len(set(all_users)) - 2:
            duos.remove(duo)

    for permutation in team_arrangements:
        team_1 = permutation[:len(permutation) // 2]
        team_2 = permutation[len(permutation) // 2:]

        team_1_ids = [user.id for user in team_1]
        team_2_ids = [user.id for user in team_2]

        duos_valid = True
        for duo in duos:
            if (len(set(team_1_ids) - set(duo)) == len(team_1_ids) - 2) or (len(set(team_2_ids) - set(duo)) == len(team_2_ids) - 2):
                pass
            else:
                duos_valid = False

        if not duos_valid:
            continue

        team_1_mmr = sum([user.get_mmr(queue_id) for user in team_1])
        team_2_mmr = sum([user.get_mmr(queue_id) for user in team_2])
        mmr_diff = abs(team_1_mmr - team_2_mmr)
        if mmr_diff < best_teams[1]:
            best_teams = [[team_1, team_2], mmr_diff]

    if best_teams[0] == None:
        raise ValueError('unable to create match')

    return best_teams
