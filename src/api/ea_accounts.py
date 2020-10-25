from flask import Blueprint
from flask import request
from flask_jwt_extended import jwt_required

from src.accounts.account_owner import check_if_user_owns_ea_account
from src.accounts.ea_account_actions import delete_ea_account_from_user, add_new_ea_account
from src.users.login import check_if_user_authenticated
from utils.nested_blueprint import NestedBlueprint

ea_accounts = Blueprint("accounts", __name__)
filters = NestedBlueprint(ea_accounts, 'search-filters')


@ea_accounts.route('/add', methods=['POST'])
@jwt_required
@check_if_user_authenticated
def add_user_ea_account(owner):
    json_data = request.get_json()
    email = json_data.get('ea_account')
    return add_new_ea_account(owner, email)


@ea_accounts.route('/delete', methods=['DELETE'])
@jwt_required
@check_if_user_authenticated
@check_if_user_owns_ea_account
def delete_user_ea_account(owner):
    json_data = request.get_json()
    email = json_data.get('email')
    return delete_ea_account_from_user(owner, email)
