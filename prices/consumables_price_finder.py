from factories.consumable_futbin_prices import ConsumableFutbinPriceFactory
from models.price_finder import FutbinPriceFinder


class ConsumablePriceFinder(FutbinPriceFinder):
    def __init__(self,item):
        self.item = item

    def get_futbin_price(self):
        return ConsumableFutbinPriceFactory(self.item).get_consumable_futbin_price()

