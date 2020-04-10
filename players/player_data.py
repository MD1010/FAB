from models.player import Player


def fill_players_value_data(user_coin_balance, requested_players, real_prices):
    result = []
    requested_players = build_player_objects_from_dict(requested_players)
    for player_obj in requested_players:
        player_market_price = 0
        for price_obj in real_prices:
            for name in price_obj.keys():
                if name == player_obj.name:
                    player_market_price = price_obj[name]
                    break
        player_obj.set_market_price(player_market_price)
        player_obj.calculate_profit(user_coin_balance)
        result.append(player_obj)
    return result


def build_player_objects_from_dict(requested_players):
    for player in requested_players:
        player_obj = Player()
        for key, value in player.items():
            setattr(player_obj, key, value)
    return requested_players
