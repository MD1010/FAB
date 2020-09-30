class EaAccount:
    def __init__(self, owner, email, password="", cookies=None):
        if cookies is None:
            cookies = []
        self.owner = owner
        self.email = email
        self.password = password
        self.cookies = cookies
        self.coins_earned = {}
        self.search_filters = []
        self.selected_filter = None

