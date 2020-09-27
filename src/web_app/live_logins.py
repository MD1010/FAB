from functools import wraps
from typing import Dict, TYPE_CHECKING

# prevent cyclic imports
from flask import request

from utils.helper_functions import server_response

if TYPE_CHECKING:
    from src.web_app.selenium_login import SeleniumLogin

authenticated_accounts: Dict[str, 'SeleniumLogin'] = {}

login_attempts: Dict[str, 'SeleniumLogin'] = {}


def check_login_attempt(func):
    @wraps(func)
    def determine_if_func_should_run(*args):
        json_data = request.get_json()
        email = json_data.get('email')
        login_attempt = login_attempts.get(email)
        if not login_attempt:
            return server_response(status='not authenticated', code=401)
        return func(login_attempt, *args)

    return determine_if_func_should_run
