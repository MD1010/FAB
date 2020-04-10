from abc import abstractmethod,ABC

from players.player_data import fill_players_value_data


def get_player_to_search(user_coin_balance, requested_players, real_prices):
    requested_players = list(fill_players_value_data(user_coin_balance, requested_players, real_prices))
    sorted_by_profit = sorted(requested_players, key=lambda player: player.profit, reverse=True)
    most_profitable_player = sorted_by_profit[0]
    # if all the players are above the budget
    if most_profitable_player.profit == 0:
        return None
    else:
        return sorted_by_profit[0]


