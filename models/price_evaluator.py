from consts.app import EA_TAX, PROFIT_MULTIPLIER
from consts.prices.prices_consts import DECREASE_SALE_PRICE_PERCENTAGE, MAX_PRICE
from factories.real_time_prices import FutbinPriceFactory
from items.item_prices import search_item_RT_price_on_market
from search_filters.filter_setter import FilterSetter


def check_items_market_prices(fab, items):
    # todo map between id and market price
    for item in items:
        # player - if the id+name is not specified then it is not specific search
        # consumable - if name is not specified then it is bot specific search
        # both cases - to check the market price name has to exist

        # if the filtered is unspecified get the min price in that filter
        if not item.get('name'):
            FilterSetter(fab.element_actions, item).set_basic_filters_to_get_item_price(MAX_PRICE, specific_player_search=False)
            FilterSetter(fab.element_actions, item).set_custom_search_filteres()
            item['marketPrice'] = search_item_RT_price_on_market(fab.element_actions, MAX_PRICE)

        if item.get('name'):
            futbin_price = FutbinPriceFactory(item, fab.user.email).get_futbin_prices_object().get_futbin_price()
            FilterSetter(fab.element_actions, item).set_basic_filters_to_get_item_price(futbin_price)
            item['marketPrice'] = search_item_RT_price_on_market(fab.element_actions, futbin_price)
            # fill the maxBIN if the user hasn't supply one

        # user_max_bin = item.get('maxBIN')
        # computed_max_bin =
        # if not user_max_bin:
        item['maxBIN'] = _get_max_buy_now_price(item['marketPrice'])
        # if the user gave a price that is higher than the computed (accidently)
        # elif user_max_bin > computed_max_bin:
        #     item['maxBIN'] = computed_max_bin


def get_sell_price(market_price):
    return market_price - (market_price * DECREASE_SALE_PRICE_PERCENTAGE)


def _get_max_buy_now_price(item_market_price):
    return item_market_price * EA_TAX - item_market_price * PROFIT_MULTIPLIER
