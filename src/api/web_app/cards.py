from flask import jsonify, request

from src.api.web_app import cards
from src.web_app.player_cards import get_all_player_cards


@cards.route('/', methods=['GET'])
def get_all_cards():
    searched_player = request.args.get('term')
    return jsonify(get_all_player_cards(searched_player))
