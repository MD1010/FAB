from flask import Blueprint, jsonify

from src.players.player_cards import get_all_players_cards

players = Blueprint("players", __name__)


@players.route('/<string:searched_player>', methods=['GET'])
def get_all_cards(searched_player):
    return jsonify(get_all_players_cards(searched_player))
