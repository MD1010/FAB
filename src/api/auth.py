from flask import Blueprint, request
from flask_jwt_extended import jwt_refresh_token_required

from src.auth.app_login import log_in_user
from src.auth.app_signup import create_new_user
from utils.helper_functions import refresh_access_token

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


@auth.route('/get-new-access-token', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    return refresh_access_token()
