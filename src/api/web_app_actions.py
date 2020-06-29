from flask import request

from src.api.web_app import actions
from src.api.web_app_login import check_login_attempt
from src.auth.web_app_login import WebAppLogin
from src.fab_loop import start_fab_loop
from src.web_app.web_app_actions import WebappActions
from utils.helper_functions import server_response
from utils.usermassinfo import get_user_ut_info


@actions.route('/get-ut-info', methods=['GET'])
@check_login_attempt
# todo split it to many routes json too big
def extract_info(login_attempt: WebAppLogin):
    return get_user_ut_info(login_attempt.email)


@actions.route('/start-loop', methods=['GET'])
@check_login_attempt
def start_loop(login_attempt: WebAppLogin):
    ea_account = login_attempt.email
    json_data = request.get_json()
    configuration = json_data['configuration']
    search_parameters = json_data['search_parameters']
    loop_result, fail_reason = start_fab_loop(ea_account, search_parameters, configuration)
    if fail_reason:
        return server_response(error=fail_reason, code=503)
    return server_response(status="Finished his job successfuly", code=200)
