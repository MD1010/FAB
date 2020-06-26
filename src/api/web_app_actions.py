from flask import request

from src.api.web_app import actions
from src.api.web_app_login import check_login_attempt
from src.auth.web_app_login import WebAppLogin
from src.fab_loop import start_fab_loop
from utils.helper_functions import server_response
from utils.usermassinfo import get_user_ut_info


@actions.route('/get-ut-info', methods=['GET'])
@check_login_attempt
# todo split it to many routes json too big
def extract_info(login_attempt: WebAppLogin):
    return get_user_ut_info(login_attempt.email)


# @actions.route('/transfer-search', methods=['GET'])
# @check_login_attempt
# def search_items(login_attempt: WebAppLogin):
#     wa = WebappActions(login_attempt.email)
#     wa.enter_first_transfer_market_search()
#     # res = wa.search_items(item_type='player', masked_def_id=158023, max_bin=2000000)
#     res = wa.search_items(item_type='player', zone="attacker",level="silver",max_bin=200)
#     auctions = sort_results_by_min_bin(res)
#     res = wa.snipe_items(auctions)
#     return "ok"

@actions.route('/start-loop', methods=['GET'])
@check_login_attempt
def start_loop(login_attempt: WebAppLogin):
    ea_account = login_attempt.email
    json_data = request.get_json()
    loop_time = json_data['time']
    configuration = json_data['configuration']
    search_parameters = json_data['search_parameters']  # example: item_type='player', zone="attacker", level="silver", max_bin=200
    loop_result, fail_reason = start_fab_loop(ea_account, search_parameters, configuration)
    if fail_reason:
        return server_response(error=fail_reason, code=503)
    return server_response(status="Not finished his job successfuly", code=200)
