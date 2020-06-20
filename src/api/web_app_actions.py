from flask import request

from src.api.web_app import actions
from src.api.web_app_login import check_login_attempt
from utils.usermassinfo import get_user_ut_info


@actions.route('/get-ut-info', methods=['GET'])
@check_login_attempt
# todo split it to many routes json too big
def extract_info(login_attempt):
    return get_user_ut_info(login_attempt.email)
