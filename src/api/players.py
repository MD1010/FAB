from flask import Blueprint, jsonify

from src.web_app.player_cards import get_all_player_cards

players = Blueprint("players", __name__)


@players.route('/<string:searched_player>', methods=['GET'])
def get_all_cards(searched_player):
    return jsonify(get_all_player_cards(searched_player))
