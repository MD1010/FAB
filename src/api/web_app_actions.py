from flask import request

from src.api.web_app import actions
from src.api.web_app_login import check_login_attempt
from src.auth.web_app_login import WebAppLogin
from src.web_app.web_app_actions import WebappActions
from utils.usermassinfo import get_user_ut_info


@actions.route('/get-ut-info', methods=['GET'])
@check_login_attempt
# todo split it to many routes json too big
def extract_info(login_attempt: WebAppLogin):
    return get_user_ut_info(login_attempt.email)

@actions.route('/transfer-search', methods=['GET'])
@check_login_attempt
def search_items(login_attempt: WebAppLogin):
    wa = WebappActions(login_attempt.email)
    wa.enter_first_transfer_market_search()
    res = wa.search_items(item_type='player', masked_def_id=158023, max_bin=200000)
    return "ok"