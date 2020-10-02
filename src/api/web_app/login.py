from flask import request

from src.api.web_app import login
from src.web_app.live_logins import check_login_attempt
from src.web_app.selenium_login import SeleniumLogin


@login.route('/launch', methods=['POST'])
# @jwt_required
# @check_if_user_authenticated
# @check_if_driver_is_already_opened
# @check_if_user_owns_ea_account
def ea_web_app_launch():
    json_data = request.get_json()
    email = json_data.get('email')
    password = json_data.get('password')
    return SeleniumLogin('MD10', email, password).start_login(email)


@login.route('/send-status-code', methods=['POST'])
@check_login_attempt
def send_status_code(login_attempt: SeleniumLogin):
    json_data = request.get_json()
    code = json_data.get('code')
    return login_attempt.set_status_code(code)
