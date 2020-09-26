from flask import jsonify, request

from src.api.web_app import entities
from src.web_app.player_cards import get_all_player_cards
from utils import db
from utils.helper_functions import get_collection_documents


@entities.route('/cards', methods=['GET'])
def get_all_cards():
    searched_player = request.args.get('term')
    return jsonify(get_all_player_cards(searched_player))


@entities.route('/leagues', methods=['GET'])
def get_all_leagues():
    return jsonify(get_collection_documents(db.leagues_collection))


@entities.route('/nations', methods=['GET'])
def get_all_nations():
    return jsonify(get_collection_documents(db.nations_collection))


@entities.route('/teams', methods=['GET'])
def get_all_clubs():
    return jsonify(get_collection_documents(db.teams_collection))
