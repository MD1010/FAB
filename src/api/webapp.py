from flask import Blueprint, request

from src.auth.ea.web_app_login import WebAppLogin

webapp = Blueprint("webapp", __name__)


@webapp.route('/login', methods=['POST'])
def ea_webapp_login():
    json_data = request.get_json()
    email = json_data.get('email')
    password = json_data.get('password')
    auth_method = json_data.get('auth_method')
    platform = json_data.get('platform')
    return WebAppLogin(email, password, platform, auth_method).launch_web_app()

