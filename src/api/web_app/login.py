from flask import request
from flask_jwt_extended import jwt_required

from src.accounts.account_owner import check_if_user_owns_ea_account, check_if_user_first_login
from src.api.web_app import login
from src.users.login import check_if_user_authenticated
from src.web_app.live_logins import check_login_attempt, authenticated_accounts
from src.web_app.selenium_login import SeleniumLogin
from utils.driver import check_if_driver_is_already_opened
from utils.helper_functions import server_response

@login.route('/connect', methods=['POST'])
@jwt_required
@check_if_user_authenticated
@check_if_user_owns_ea_account
@check_if_driver_is_already_opened
@check_if_user_first_login
def ea_web_app_launch(owner, email, password):
    return SeleniumLogin(owner, email, password).web_app_login(email)

@login.route('/first-login', methods=['POST'])
@jwt_required
@check_if_user_authenticated
@check_if_user_owns_ea_account
@check_if_driver_is_already_opened
def ea_web_app_first_login(owner):
    json_data = request.get_json()
    email = json_data.get('email')
    password = json_data.get('password')
    return SeleniumLogin(owner, email, password).web_app_login(email)

@login.route('/connect-with-code', methods=['POST'])
@jwt_required
@check_if_user_authenticated
@check_if_user_owns_ea_account
@check_login_attempt
def send_status_code(login_attempt: SeleniumLogin):
    json_data = request.get_json()
    code = json_data.get('code')
    return login_attempt.login_with_code(login_attempt.email, code)

@login.route('/disconnect', methods=['POST'])
@jwt_required
@check_if_user_authenticated
@check_if_user_owns_ea_account
def ea_web_app_disconnect(owner):
    json_data = request.get_json()
    email = json_data.get('email')
    if not authenticated_accounts.get(email):
        return server_response(code=403, msg="Account is already disconnected")
    authenticated_user = authenticated_accounts.get(email)
    return authenticated_user.disconnect()
