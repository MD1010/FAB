import json

import requests

from consts.app import FUTHEAD_PLAYER
from players.player import Player


def build_player_objects(requested_players, real_prices):
    result = []
    for player in requested_players:
        player_name = player["name"]
        rating = player["rating"]
        specific_card_id = player["id"]
        revision = player["revision"]
        name = player["name"]
        nation = player["nation"]
        position = player["position"]
        club = player["club"]

        player_market_price = 0
        for price_obj in real_prices:
            for name in price_obj.keys():
                if name == player_name:
                    player_market_price = price_obj[player_name]
                    break
        player_obj = Player(specific_card_id, player_name, rating, revision, nation, position, club)
        player_obj.set_market_price(player_market_price)
        player_obj.calculate_profit()
        result.append(player_obj)
    return result


def get_cards_from_the_same_player(ea_player_data):
    player_full_name = ea_player_data.get("name")
    player_id = ea_player_data.get("id")
    # go to futhead to find all cards of that player
    futhead_url_player_data = f'{FUTHEAD_PLAYER}{player_full_name}'
    details_of_specific_player = json.loads(requests.get(futhead_url_player_data).content)

    cards_from_the_same_id = []
    for player_in_json_futhead in details_of_specific_player:
        if player_in_json_futhead["player_id"] == player_id:
            rating = player_in_json_futhead["rating"]
            specific_card_id = player_in_json_futhead["def_id"]
            revision = player_in_json_futhead["revision_type"]
            name = player_in_json_futhead["full_name"]
            nation = player_in_json_futhead["nation_name"]
            position = player_in_json_futhead["position"]
            club = player_in_json_futhead["club_name"]
            cards_from_the_same_id.append(Player(specific_card_id, name, rating, revision, nation, position, club))
    return cards_from_the_same_id
