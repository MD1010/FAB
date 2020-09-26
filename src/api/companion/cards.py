from flask import Blueprint, jsonify, request

from src.web_app.player_cards import get_all_player_cards

cards = Blueprint("cards", __name__)


@cards.route('/', methods=['GET'])
def get_all_cards():
    searched_player = request.args.get('term')
    return jsonify(get_all_player_cards(searched_player))
