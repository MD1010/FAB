from flask import Blueprint
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from users.user_ea_accounts import add_ea_account_to_user, delete_ea_account_from_user

ea_accounts = Blueprint("ea_accounts", __name__)


@ea_accounts.route('/login', methods=['POST'])
@jwt_required
def ea_account_login():
    return ""


@ea_accounts.route('/add', methods=['POST'])
@jwt_required
def add_user_ea_account():
    json_data = request.get_json()
    username = get_jwt_identity()['username']
    ea_account = json_data.get('ea_account')
    return add_ea_account_to_user(username, ea_account)


@ea_accounts.route('/delete', methods=['DELETE'])
@jwt_required
def delete_user_ea_account():
    json_data = request.get_json()
    username = get_jwt_identity()['username']
    ea_account = json_data.get('ea_account')
    return delete_ea_account_from_user(username, ea_account)
