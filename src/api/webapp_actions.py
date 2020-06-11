from consts import REQUEST_TIMEOUT, GAME_URL
from src.api.webapp import actions
from src.api.webapp_login import check_login_attempt
from src.auth.webapp_login import WebAppLogin

@actions.route('/get-ut-info', methods=['GET'])
@check_login_attempt
# todo split it to many routes json too big
def get_user_ut_info():
    fut_host = WebAppLogin.get_instance().fut_host
    request_session = WebAppLogin.get_instance().request_session
    return request_session.get(f'https://{fut_host}/{GAME_URL}/usermassinfo', timeout=REQUEST_TIMEOUT).json()
