from flask import request

from src.api.webapp import actions
from src.api.webapp_login import check_login_attempt
from utils.common_requests import get_user_ut_info


@actions.route('/get-ut-info', methods=['GET'])
@check_login_attempt
# todo split it to many routes json too big
def extract_info(login_attempt):
    return get_user_ut_info(login_attempt.email)
