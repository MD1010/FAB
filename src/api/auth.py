from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_refresh_token_required, jwt_required
from consts import server_status_messages
from src.users.login import log_in_user, check_if_user_authenticated
from src.users.signup import create_new_user
from utils.helper_functions import server_response
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


@auth.route('/refresh', methods=['POST'])
def refresh_token():
    token = request.cookies.get('refresh_token')
    json_data = request.get_json()
    username = json_data.get('username')
    if not token:
        return server_response(msg=server_status_messages.REFRESH_TOKEN_REQUIRED,code=400)
    if token not in refresh_tokens.get(username):
        return server_response(msg=server_status_messages.INVALID_REFRESH_TOKEN, code=400)
    return refresh_access_token(username)
