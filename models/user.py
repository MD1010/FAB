class User:
    def __init__(self, email, password="", cookies=None, username="", platform=""):
        if cookies is None:
            cookies = []
        self.email = email
        self.password = password
        self.cookies = cookies
        self.username = username
        self.platform = platform
        self.total_runtime = 0
        self.coin_balance = 0
        self.coins_earned = 0