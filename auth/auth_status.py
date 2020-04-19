from live_data import ea_account_login_attempts


def set_auth_status(email, is_auth):
    ea_account_login_attempts[email].is_authenticated = is_auth


def set_web_app_status(email, is_up):
    ea_account_login_attempts[email].web_app_ready = is_up
