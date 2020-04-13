from enums.item_types import ItemTypes
from prices.consumables_price_finder import ConsumablePriceFinder
from prices.player_futbin_price_finder import PlayerFutbinPriceFinder


class FutbinPriceFactory:
    def __init__(self, item,user_email):
        self.item = item
        self.user_email = user_email

    def get_futbin_prices_object(self):
        rt_prices_instances = {
            ItemTypes.PLAYER: PlayerFutbinPriceFinder(self.item,self.user_email)
        }
        # default is consumable price finder
        return rt_prices_instances.get(ItemTypes(self.item['type']), ConsumablePriceFinder(self.item))
