import json
import re

import requests

from consts import FUTHEAD_PLAYER_SEARCH, FUTWIZ_PLAYER_SEARCH, FUTBIN_PLAYER_SEARCH


def _get_combined_data_from_futbin_and_futwiz(searched_player_name_string):
    futwiz_url_player_data = f'{FUTWIZ_PLAYER_SEARCH}{searched_player_name_string}'
    futbin_url_player_data = f'{FUTBIN_PLAYER_SEARCH}{searched_player_name_string}'
    futwiz_data = json.loads(requests.get(futwiz_url_player_data).content)
    futbin_data = json.loads(requests.get(futbin_url_player_data).content)
    existing_cards = []
    if futwiz_data and futbin_data:
        for futwiz_record in futwiz_data:
            for futbin_record in futbin_data:
                """
                    stupid way to check if this is the same card in futwiz and futbin because we need to extract
                    from futwiz the def_if and the rest from futbin and there is not similar identifier between both sites..
                    so if the card type(rare) the position and the rating are similar let me believe this is the same card
                    it will enter this kind of search only when the card is not found in futhead so let it be...
                """
                #
                if futwiz_record['rare'] == futbin_record['rare_type'] and \
                        futwiz_record['position'] == futbin_record['position'] and \
                        futwiz_record['rating'] == futbin_record['rating']:
                    # for cases that the players has strange p in the altimage like Ronaldo PRIME MOMENTS
                    # take the def_id from futwiz
                    futwiz_def_id = int(re.sub('[a-zA-Z?!.,;]', '', futwiz_record['alt_img'])) if futwiz_record.get("alt_img") else futwiz_record["pid"]
                    # if player_in_json_futhead["player_id"] == player_id:
                    player_card = {
                        'id': futwiz_def_id,
                        'name': futwiz_record["name"],
                        'revision': futwiz_record['cardtype'],
                        'rating': int(futwiz_record["rating"]),
                        'position': futwiz_record["position"],
                        'clubImage': futbin_record["club_image"],
                        'nationImage': futbin_record["nation_image"],
                        'playerImage': futbin_record["image"]
                    }
                    existing_cards.append(player_card)
    return existing_cards


def _get_data_from_futhead(searched_player_name_string):
    futhead_url_player_data = f'{FUTHEAD_PLAYER_SEARCH}{searched_player_name_string}'
    existing_cards = []
    futhead_data = json.loads(requests.get(futhead_url_player_data).content)
    if futhead_data:
        for futhead_record in futhead_data:
            # if player_in_json_futhead["player_id"] == player_id:
            player_card = {
                'id': futhead_record["def_id"],
                'name': futhead_record["full_name"],
                'revision': futhead_record["revision_type"],
                'rating': futhead_record["rating"],
                'position': futhead_record["position"],
                'clubImage': futhead_record["club_image"],
                'nationImage': futhead_record["nation_image"],
                'playerImage': futhead_record["image"]
            }
            existing_cards.append(player_card)
    return existing_cards


def get_all_player_cards(searched_player_name_string):
    existing_cards = _get_data_from_futhead(searched_player_name_string)
    if existing_cards: return existing_cards
    # if no results were found in futhead check futwiz
    return _get_combined_data_from_futbin_and_futwiz(searched_player_name_string)
