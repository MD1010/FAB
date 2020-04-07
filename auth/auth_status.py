from active.data import user_login_attempts


def set_auth_status(email, is_auth):
    user_login_attempts[email].is_authenticated = is_auth


def set_web_app_status(email, is_up):
    user_login_attempts[email].web_app_ready = is_up
