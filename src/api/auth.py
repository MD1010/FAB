from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_refresh_token_required, jwt_required, get_jwt_identity

from consts import server_status_messages
from src.users.login import log_in_user, check_if_user_authenticated
from src.users.signup import create_new_user
from utils.tokens import refresh_access_token, access_tokens, refresh_tokens

auth = Blueprint("auth", __name__)


@auth.route('/signup', methods=['POST'])
def sign_up_user():
    json_data = request.get_json()
    username = json_data.get('username')
    password = json_data.get('password')
    return create_new_user(username, password)


@auth.route('/login', methods=['POST'])
def login():
    json_data = request.get_json()
    username = json_data.get('username')
    password = json_data.get('password')
    return log_in_user(username, password)


@auth.route('/logout', methods=['POST'])
@jwt_required
@check_if_user_authenticated
def logout(username):
    access_tokens.pop(username)
    refresh_tokens.pop(username)
    return jsonify(msg=server_status_messages.LOGOUT_SUCCESS)


@auth.route('/get-new-access-token', methods=['POST'])
@jwt_refresh_token_required
@check_if_user_authenticated
def refresh_token(username):
    return refresh_access_token()
