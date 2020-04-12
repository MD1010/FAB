import json
from multiprocessing.pool import ThreadPool

import requests

from consts.app import FUTHEAD_PLAYER
from models.player import Player
from utils import db


def _get_player_full_futhead_data(contain_searched_term_players):
    if len(contain_searched_term_players) == 0: return []
    player_thread_pool = ThreadPool(len(contain_searched_term_players))
    players_imap_iterator = player_thread_pool.imap(get_cards_from_the_same_player, contain_searched_term_players)
    player_thread_pool.close()
    player_thread_pool.join()
    result = []
    for _, player_record in players_imap_iterator._items:
        if len(player_record) > 0:
            for player_data in player_record:
                result.append(player_data)
    return result


def get_all_players_cards(searched_player_name_string):
    contain_searched_term_players = list(
        db.players_collection.find({"name": {'$regex': f".*{searched_player_name_string}.*", '$options': 'i'}}).limit(20).sort('rating', -1))
    unsorted_result = _get_player_full_futhead_data(contain_searched_term_players)
    sorted_by_rating_result = sorted(unsorted_result, key=lambda player: player.rating, reverse=True)
    return sorted_by_rating_result


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
            position = player_in_json_futhead["position"]
            club_img = player_in_json_futhead["club_image"]
            nation_image = player_in_json_futhead["nation_image"]
            player_image = player_in_json_futhead["image"]
            cards_from_the_same_id.append(Player(specific_card_id, name, rating, revision, position, player_image, club_img, nation_image))
    return cards_from_the_same_id
