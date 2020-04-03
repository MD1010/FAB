import time


class LoginAttempt:
    def __init__(self):
        self.is_authenticated = False
        self.timer = time.time()


