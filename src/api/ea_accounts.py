from flask import Blueprint
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.accounts.ea_account_actions import delete_ea_account_from_user
from src.users.login import check_if_user_authenticated

ea_accounts = Blueprint("ea_accounts", __name__)


@ea_accounts.route('/delete', methods=['DELETE'])
@jwt_required
@check_if_user_authenticated
def delete_user_ea_account():
    json_data = request.get_json()
    username = get_jwt_identity()['username']
    ea_account = json_data.get('ea_account')
    return delete_ea_account_from_user(username, ea_account)
