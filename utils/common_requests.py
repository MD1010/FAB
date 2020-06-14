from consts import GAME_URL, REQUEST_TIMEOUT
from src.auth.live_logins import authenticated_accounts


def get_user_ut_info(email, info_type=None):
    fut_host = authenticated_accounts.get(email).fut_host
    request_session = authenticated_accounts.get(email).request_session
    if not info_type:
        return request_session.get(f'https://{fut_host}/{GAME_URL}/usermassinfo', timeout=REQUEST_TIMEOUT).json()
    else:
        return request_session.get(f'https://{fut_host}/{GAME_URL}/usermassinfo', timeout=REQUEST_TIMEOUT).json()[info_type]
    # possibly can return this:
    # {
    #     "reason": "expired session",
    #     "message": null,
    #     "code": 401
    # }
