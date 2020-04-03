from active.data import users_attempted_login


def set_auth_status(email, is_auth):
    users_attempted_login[email].is_authenticated = is_auth