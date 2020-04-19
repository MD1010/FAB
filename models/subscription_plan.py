from consts.subscription_plans import plan_expiration_dates, plan_accounts_limit


class SubscriptionPlan:
    def __init__(self, plan_type):
        self.plan_type = plan_type
        self.expiry_date = plan_expiration_dates[plan_type]
        self.accounts_limit = plan_accounts_limit[plan_type]
