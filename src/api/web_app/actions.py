from flask import request
from src.api.web_app.index import actions
from src.api.web_app.login import check_login_attempt
from src.web_app.selenium_login import SeleniumLogin
from src.web_app.fab_loop import start_loop_run
from utils.helper_functions import server_response
from src.web_app.live_logins import authenticated_accounts


@actions.route('/start-loop', methods=['POST'])
def start_loop():
    json_data = request.get_json()
    email = json_data['email']
    if not authenticated_accounts.get(email):
        return server_response(code=403, msg="Please connect first before running")
    configuration = json_data['configuration']
    search_parameters = json_data['search_parameters']
    return start_loop_run(authenticated_accounts.get(email), search_parameters, configuration)
