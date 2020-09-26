from flask import request
from src.api.web_app.index import actions
from src.api.web_app.login import check_login_attempt
from src.auth.selenium_login import SeleniumLogin
from src.fab_loop import start_fab_loop
from utils.helper_functions import server_response


@actions.route('/start-loop', methods=['GET'])
@check_login_attempt
def start_loop(login_attempt: SeleniumLogin):
    ea_account = login_attempt.email
    json_data = request.get_json()
    configuration = json_data['configuration']
    search_parameters = json_data['search_parameters']
    loop_result, fail_reason = start_fab_loop(ea_account, search_parameters, configuration)
    if fail_reason:
        return server_response(error=fail_reason, code=503)
    return server_response(status="Finished his job successfuly", code=200)
