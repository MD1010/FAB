import time

from consts.app import STATUS_CODE_TRIES


class LoginAttempt:
    def __init__(self):
        self.is_authenticated = False
        self.timer = time.time()
        self.tries_with_status_code = STATUS_CODE_TRIES

