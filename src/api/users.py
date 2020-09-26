from flask import Blueprint
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.users.user_details import update_user_username, update_user_password

users = Blueprint("users", __name__)


@users.route("/update-username", methods=['PUT'])
@jwt_required
def edit_username():
    json_data = request.get_json()
    # make sure to log again to fetch an updated useraname
    old_username = get_jwt_identity()['username']
    new_username = json_data.get('new_username')
    return update_user_username(old_username, new_username)


@users.route('/update-password', methods=['PUT'])
@jwt_required
def edit_password():
    json_data = request.get_json()
    username = get_jwt_identity()['username']
    new_password = json_data.get('new_password')
    return update_user_password(username, new_password)

