from flask import jsonify, Blueprint
from flask import request
from flask_jwt_extended import jwt_required

from src.accounts.ea_account_actions import get_owner_accounts
from src.users.login import check_if_user_authenticated
from src.web_app.player_cards import get_all_player_cards
from utils import db
from utils.db import get_collection_documents

entities = Blueprint("entities", __name__)

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
def get_all_teams():
    return jsonify(get_collection_documents(db.teams_collection))

@entities.route('/accounts', methods=['GET'])
@jwt_required
@check_if_user_authenticated
def get_all_user_accounts(owner):
    return jsonify(get_owner_accounts(owner))
