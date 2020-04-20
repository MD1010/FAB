class User:
    def __init__(self, username, password, plan, ea_accounts=None):
        if ea_accounts is None:
            ea_accounts = []
        self.plan = plan
        self.password = password
        self.ea_accounts = ea_accounts
        self.username = username
