from consts.app import EA_TAX, PROFIT_MULTIPLIER
from consts.prices.prices_consts import DECREASE_SALE_PRICE_PERCENTAGE


class Item:
    def __init__(self, id='', name='', type='', user_max_bin=0):
        self.type = type
        self.id = id
        self.name = name
        self.profit = 0
        self.market_price = 0
        self.max_buy_price = user_max_bin

    def set_market_price(self, market_price):
        self.market_price = market_price

    def get_sell_price(self):
        return self.market_price - (self.market_price * DECREASE_SALE_PRICE_PERCENTAGE)

    def set_max_buy_now_price(self):
        self.max_buy_price = self.market_price * EA_TAX - self.market_price * PROFIT_MULTIPLIER

    def calculate_profit(self, user_coin_balance):
        # if the user costs more than the user can afford then no profit can be made
        if self.max_buy_price > user_coin_balance:
            self.profit = 0
        else:
            self.profit = self.market_price - self.get_sell_price()