from consts.item_types import ItemTypes
from rt_prices.consumable_styles_price_finder import ConsumablePriceFinder
from rt_prices.player_real_time_price_finder import PlayerFutbinPriceFinder


class FutbinPriceFactory:
    def __init__(self, item):
        self.item = item

    def get_futbin_prices_class(self):
        rt_prices_instances = {
            ItemTypes.PLAYER: PlayerFutbinPriceFinder()
        }
        # default is consumable price finder
        rt_prices_instances.get(self.item.type, ConsumablePriceFinder())
