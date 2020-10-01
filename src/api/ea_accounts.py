from flask import Blueprint
from flask import request
from flask_jwt_extended import jwt_required

from src.accounts.account_owner import check_if_user_owns_ea_account
from src.accounts.ea_account_actions import delete_ea_account_from_user, get_owner_accounts
from src.users.login import check_if_user_authenticated
from utils.nested_blueprint import NestedBlueprint

ea_accounts = Blueprint("ea_accounts", __name__)
filters = NestedBlueprint(ea_accounts, 'search-filters')

@ea_accounts.route('/', methods=['GET'])
@jwt_required
@check_if_user_authenticated
def get_all_user_accounts(owner):
    return get_owner_accounts(owner)


@ea_accounts.route('/delete', methods=['DELETE'])
@jwt_required
@check_if_user_authenticated
@check_if_user_owns_ea_account
def delete_user_ea_account(owner):
    json_data = request.get_json()
    email = json_data.get('ea_account')
    return delete_ea_account_from_user(owner, email)

