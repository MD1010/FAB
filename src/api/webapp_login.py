from functools import wraps

from flask import request

from src.api.webapp import login
from src.auth.ea.webapp_login import WebAppLogin
from utils.helper_functions import server_response

def check_login_attempt(func):
    @wraps(func)
    def  determine_if_func_should_run(*args):
        if WebAppLogin.get_instance() is None:
            return server_response(status='not authenticated', code=401)
        if WebAppLogin.get_instance().entered_correct_creadentials is False:
            return server_response(status='not authenticated', code=401)
        return func(*args)
    return determine_if_func_should_run

@login.route('/verify-client', methods=['POST'])
def ea_webapp_login():
    json_data = request.get_json()
    email = json_data.get('email')
    password = json_data.get('password')
    platform = json_data.get('platform')
    auth_method = json_data.get('auth_method')
    return WebAppLogin(email, password, platform, auth_method).verify_client()

@login.route('/get-status-code', methods=['GET'])
@check_login_attempt
def get_status_code():
    login_attempt = WebAppLogin.get_instance()
    return login_attempt.get_verification_code()

@login.route('/set-status-code', methods=['POST'])
@check_login_attempt
def send_status_code():
    json_data = request.get_json()
    code = json_data.get('code')
    login_attempt = WebAppLogin.get_instance()
    return login_attempt.set_verification_code(code)
