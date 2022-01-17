# using elo at the moment
k_value = 32

def mmr(teams, winner, scores):
    win_amt = abs(scores[0] - scores[1]) / 10 * 0.3 + 0.7
    team_averages = [sum(teams[0]) / len(teams[0]), sum(teams[1]) / len(teams[1])]
    transformed_ratings = [10 ** (team_averages[0] / 400), 10 ** (team_averages[1] / 400)]
    expected_scores = [
        transformed_ratings[0] / (transformed_ratings[0] + transformed_ratings[1]),
        transformed_ratings[1] / (transformed_ratings[1] + transformed_ratings[0]),
    ]
    if winner == 0:
        mmr_scores = [win_amt, 1 - win_amt]
    else:
        mmr_scores = [1 - win_amt, win_amt]

    mmr_change = [k_value * (mmr_scores[0] - expected_scores[0]), k_value * (mmr_scores[1] - expected_scores[1])]

    return mmr_change
