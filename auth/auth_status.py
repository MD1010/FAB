from active.data import user_login_attempts


def set_auth_status(email, is_auth):
    user_login_attempts[email].is_authenticated = is_auth