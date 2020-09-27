from flask import Blueprint
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from consts import server_status_messages
from src.users.login import check_if_user_authenticated
from src.users.user_details import update_user_username, update_user_password
from utils.helper_functions import server_response

users = Blueprint("users", __name__)


@users.route("/update-username", methods=['PUT'])
@jwt_required
@check_if_user_authenticated
def edit_username(username):
    json_data = request.get_json()
    # make sure to log again to fetch an updated useraname
    if json_data.get('username') != username:
        return server_response(status=server_status_messages.AUTH_FAILED, code=401)
    new_username = json_data.get('new_username')
    return update_user_username(username, new_username)


@users.route('/update-password', methods=['PUT'])
@jwt_required
@check_if_user_authenticated
def edit_password(username):
    json_data = request.get_json()
    if json_data.get('username') != username:
        return server_response(status=server_status_messages.AUTH_FAILED, code=401)
    new_password = json_data.get('new_password')
    return update_user_password(username, new_password)

