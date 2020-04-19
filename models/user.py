class User:
    def __init__(self, username, password, plan, user_ea_accounts=None):
        if user_ea_accounts is None:
            user_ea_accounts = []
        self.plan = plan
        self.user_ea_accounts = user_ea_accounts
        self.username = username
