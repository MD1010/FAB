from consts.app import EA_TAX, PROFIT_MULTIPLIER
from consts.prices.prices_consts import DECREASE_SALE_PRICE_PERCENTAGE, MAX_PRICE
from factories.real_time_prices import FutbinPriceFactory
from items.item_prices import search_item_RT_price_on_market
from search_filters.filter_setter import FilterSetter


def check_items_market_prices(fab, items):
    for item in items:
        item_start_price_limit = FutbinPriceFactory(item, fab.user.email).get_futbin_prices_object().get_futbin_price() if item.get('name') else MAX_PRICE
        # the filter will be set according to the item maxBIN
        item['maxBIN'] = item_start_price_limit
        FilterSetter(fab.element_actions, item).set_search_filteres()
        item['marketPrice'] = search_item_RT_price_on_market(fab.element_actions, item_start_price_limit)
        item['maxBIN'] = _get_max_buy_now_price(item['marketPrice'])


def get_sell_price(market_price):
    return market_price - (market_price * DECREASE_SALE_PRICE_PERCENTAGE)


def _get_max_buy_now_price(item_market_price):
    return item_market_price * EA_TAX - item_market_price * PROFIT_MULTIPLIER
