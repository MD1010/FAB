from consts.app import EA_TAX, PROFIT_MULTIPLIER
from consts.prices.prices_consts import DECREASE_SALE_PRICE_PERCENTAGE


class Item:
    def __init__(self, id='', name='', type=''):
        self.type = type
        self.id = id
        self.name = name
        self.profit = 0
        self.market_price = 0
        self.sell_price = 0

    def set_market_price(self, market_price):
        self.market_price = market_price

    def set_sell_price(self):
        self.sell_price = self.market_price - (self.market_price * DECREASE_SALE_PRICE_PERCENTAGE)

    def calculate_profit(self, user_coin_balance):
        # if the user costs more than the user can afford then no profit can be made
        if self.get_max_buy_now_price() > user_coin_balance:
            self.profit = 0
        else:
            self.profit = self.market_price - self.sell_price

    def get_max_buy_now_price(self):
        return self.market_price * EA_TAX - self.market_price * PROFIT_MULTIPLIER
