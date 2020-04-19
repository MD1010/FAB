from consts.app import EA_TAX, PROFIT_MULTIPLIER
from consts.prices.prices_consts import DECREASE_SALE_PRICE_PERCENTAGE, MAX_PRICE, MAP_INC_DEC_PRICES
from factories.real_time_prices import FutbinPriceFactory
from items.item_prices import search_item_RT_price_on_market
from search_filters.filter_setter import FilterSetter


def check_items_market_prices(fab, items):
    for item in items:
        item_start_price_limit = FutbinPriceFactory(item, fab.ea_account.email).get_futbin_prices_object().get_futbin_price() if item.get('name') else MAX_PRICE
        # the filter will be set according to the item maxBIN
        item['maxBIN'] = item_start_price_limit
        FilterSetter(fab.element_actions, item).set_search_filteres()
        item['marketPrice'] = search_item_RT_price_on_market(fab, item_start_price_limit)
        item['maxBIN'] = _get_max_buy_now_price(item['marketPrice'])


def get_sell_price(market_price):
    list_price = market_price - (market_price * DECREASE_SALE_PRICE_PERCENTAGE)
    for element in MAP_INC_DEC_PRICES.items():
        values = element[0].split("-")
        if float(values[0]) < list_price < float(values[1]):
            scale = float(element[1])
            break
    deviation = list_price % scale
    if deviation == scale / 2:
        list_price = list_price + deviation
    elif deviation > scale / 2:
        list_price = list_price - deviation + scale
    else:
        list_price = list_price - deviation
    return list_price


def _get_max_buy_now_price(item_market_price):
    return item_market_price * EA_TAX - item_market_price * PROFIT_MULTIPLIER
