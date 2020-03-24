from consts.app import EA_TAX, PROFIT_MULTIPLIER
from consts.prices import DECREASE_SALE_PRICE_PERCENTAGE
from user_info import user


class Player:
    def __init__(self, id, name, rating, revision, market_price):
        self.id = id
        self.name = name
        self.rating = rating
        self.revision = revision
        self.market_price = market_price
        self.profit = 0
        self.max_buy_price = 0
        self.sell_price = 0

        self._calculate_max_buy_price()
        self._calculate_profit()

    def _calculate_max_buy_price(self):
        self.max_buy_price = self.market_price * EA_TAX - self.market_price * PROFIT_MULTIPLIER

    def get_sell_price(self):
        self.sell_price = self.market_price - (self.market_price * DECREASE_SALE_PRICE_PERCENTAGE)

    def _calculate_profit(self):
        # if the user costs more than the user can afford then no profit can be made
        if self.max_buy_price > user.coin_balance:
            self.profit = 0
        else:
            self.profit = self.market_price - self.sell_price

    def __repr__(self):
        print({
            'id': self.id,
            'name': self.name,
            'rating': self.rating,
            'market_price': self.market_price,
        })

    def player_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'rating': self.rating,
            'market_price': self.market_price,
        }
