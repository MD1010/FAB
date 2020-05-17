from flask import request

from src.api.webapp import login
from src.auth.ea.webapp_login import WebAppLogin


@login.route('/launch', methods=['POST'])
def ea_webapp_login():
    json_data = request.get_json()
    email = json_data.get('email')
    password = json_data.get('password')
    platform = json_data.get('platform')
    auth_method = json_data.get('auth_method')
    return WebAppLogin(email, password, platform, auth_method).launch_webapp()

@login.route('/set-status-code', methods=['GET'])
def send_status_code():
    json_data = request.get_json()
    code = json_data.get('code')
    login_attempt = WebAppLogin.get_instance()
    return login_attempt.set_verification_code(code)
