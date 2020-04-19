from enums.item_types import ItemTypes
from prices.consumables_price_finder import ConsumablePriceFinder
from prices.player_futbin_price_finder import PlayerFutbinPriceFinder


class FutbinPriceFactory:
    def __init__(self, item, ea_account_email):
        self.item = item
        self.ea_account_email = ea_account_email

    def get_futbin_prices_object(self):
        rt_prices_instances = {
            ItemTypes.PLAYER: PlayerFutbinPriceFinder(self.item, self.ea_account_email)
        }
        # default is consumable price finder
        return rt_prices_instances.get(ItemTypes(self.item['type']), ConsumablePriceFinder(self.item))
