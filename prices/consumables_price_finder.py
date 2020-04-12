from factories.consumable_futbin_prices import ConsumableFutbinPriceFactory
from models.price_finder import FutbinPriceFinder


class ConsumablePriceFinder(FutbinPriceFinder):
    def get_futbin_price(self, item, user_email):
        consumable_factory = ConsumableFutbinPriceFactory(item)
        return consumable_factory.get_consumable_futbin_price()
