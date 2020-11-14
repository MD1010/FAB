from flask import request
from flask_jwt_extended import jwt_required

from src.accounts.account_owner import check_if_user_owns_ea_account
from src.accounts.ea_account_actions import add_search_filter_to_account, remove_search_filter_to_account, set_selected_filter
from src.api.ea_accounts import filters
from src.users.login import check_if_user_was_authenticated


@filters.route('/add-filter', methods=['POST'])
@jwt_required
@check_if_user_was_authenticated
@check_if_user_owns_ea_account
def add_search_filter(owner):
    json_data = request.get_json()
    email = json_data.get('email')
    search_filter = json_data.get('filter')
    return add_search_filter_to_account(email, search_filter)


@filters.route('/remove-filter', methods=['POST'])
@jwt_required
@check_if_user_was_authenticated
@check_if_user_owns_ea_account
def remove_search_filter(owner):
    json_data = request.get_json()
    email = json_data.get('email')
    filter_id = json_data.get('filter_id')
    return remove_search_filter_to_account(email, filter_id)


@filters.route('/set-selected-filter', methods=['POST'])
@jwt_required
@check_if_user_was_authenticated
@check_if_user_owns_ea_account
def set_selected_search_filter(owner):
    json_data = request.get_json()
    email = json_data.get('email')
    filter_id = json_data.get('filter_id')
    return set_selected_filter(email, filter_id)
