import random
import time

from consts import MAX_PRICE, BOTTOM_LIMIT_MAX_PRICE, AMOUNT_OF_SEARCHES_BEFORE_SLEEP, SLEEP_MID_OPERATION_DURATION
from src.web_app.actions import WebAppActions
from src.web_app.auction_helpers import sort_results_by_min_bin
from src.web_app.price_evaluator import get_max_buy_now_price
from src.web_app.selenium_login import SeleniumLogin
from utils.exceptions import FutError


def start_fab_loop(ea_account: SeleniumLogin, search_parameters, configuration):
    keepalive_requests_count = 1  # send settings request every 10 minutes every request up the counter
    keepalive_request_interval = 600  # every ten minutes - settings / config.json
    loop_time = configuration['time']
    is_random_snipe = configuration['randomSnipe']  # maybe bid
    is_list_after_buy = configuration['list']
    search_count = 1
    try:
        web_app_actions = WebAppActions(ea_account)
        start_time = time.time()
        web_app_actions.enter_first_transfer_market_search()  # just pin events
        while True:
            curr_time = time.time()
            elapsed_time = curr_time - start_time
            if elapsed_time > loop_time: break  # loop finished

            # send "keepalives"
            if elapsed_time > keepalive_requests_count * keepalive_request_interval:  # just send every 10 minutes to keep alive
                print("sending settings request")
                web_app_actions.make_settings_request()
                keepalive_requests_count += 1
            if elapsed_time > keepalive_requests_count * keepalive_request_interval * 3:  # just send every 30 minutes to keep alive
                print("sending remote.json request")
                web_app_actions.make_remote_config_request()
                keepalive_requests_count += 1

            # respect interval between requests
            time.sleep(random.uniform(1, 1.5))
            print(f"search number {search_count}")

            # to make the market refresh - randomize the decreases to not get temp ban from searching

            search_parameters["max_price"] = MAX_PRICE - random.randint(1, 3) * 1000  # random the decrease to not be suspecious
            if search_parameters["max_price"] <= BOTTOM_LIMIT_MAX_PRICE: search_parameters["max_price"] = MAX_PRICE

            if not is_random_snipe:  # buying certain player
                market_price = web_app_actions.get_item_min_price(search_parameters["def_id"])
                search_parameters["max_bin"] = get_max_buy_now_price(market_price)

            results = web_app_actions.search_items(**search_parameters)
            if results:
                sorted_results = sort_results_by_min_bin(results)
                succrssful_bids = web_app_actions.snipe_items(sorted_results)
                if is_list_after_buy:
                    for item in succrssful_bids:
                        web_app_actions.list_item(item.item_id, item.def_id)
                else:
                    web_app_actions.send_item_to_trade_pile(succrssful_bids)
            else:
                print(f"No results 😑")
            web_app_actions.send_back_to_new_search_pin_event()

            # to not overload with requests
            if search_count % AMOUNT_OF_SEARCHES_BEFORE_SLEEP == 0:
                print("sleeping after amount of searches...")
                time.sleep(SLEEP_MID_OPERATION_DURATION)
            search_count += 1
    except FutError as e:
        return False, e.reason
    return True, None
