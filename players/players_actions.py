import time

from selenium.webdriver.common.keys import Keys

from consts import elements
from consts.app import MIN_PRICE, NUMBER_OF_SEARCHS_BEFORE_BINARY_SEARCH, MAP_INC_DEC_PRICES, MIN_PLAYER_PRICE
from driver import Driver
from elements.elements_manager import ElementCallback, ElementActions
from players.player_search import get_approximate_min_price


class PlayerActions(Driver):
    def __init__(self, driver):
        self.driver = driver
        super().__init__(driver)
        self.element_actions = ElementActions(self.driver)

    def init_search_player_info(self, player_name, player_price):
        # write the searched player name
        self.element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        time.sleep(1)
        self.element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS, player_name)
        # while self.element_actions.get_element(elements.SEARCHED_PLAYER_FIELD).get_attribute('value') != player_name:
        #     pass
        # choose the player in the list(the first one)
        self.element_actions.execute_element_action(elements.FIRST_RESULT_INPUT_SEARCH, ElementCallback.CLICK)
        # set max BIN price - clear the input first
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, player_price)

        max_price_input = self.element_actions.get_element(elements.MAX_BIN_PRICE_INPUT).get_attribute('value')
        if max_price_input != player_price:
            return False
        # self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
        return True

    def buy_player(self):
        no_results_banner = self.element_actions.get_element(elements.NO_RESULTS_FOUND)
        # not enoght money left
        if no_results_banner:
            return False
        if not no_results_banner:
            buy_btn = self.element_actions.get_element(elements.BUY_BTN)
            can_buy = buy_btn.is_enabled() if buy_btn else False
            if can_buy:
                self.element_actions.execute_element_action(elements.BUY_BTN, ElementCallback.CLICK)
                self.element_actions.execute_element_action(elements.CONFIRM_BUY_BTN, ElementCallback.CLICK)
                return True
            else:
                return False

    def list_player(self, price):
        # check if elemenet is listable - maybe if the time has expired..
        list_element = self.element_actions.get_element(elements.LIST_ON_TRANSFER_BTN)
        if not list_element:
            return
        # Button to start the listing quickly after buying (not through user transfer list)
        self.element_actions.execute_element_action(elements.LIST_ON_TRANSFER_BTN, ElementCallback.CLICK)
        # adjust BIN

        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, price)
        # adjust starting BIN
        self.element_actions.execute_element_action(elements.MIN_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        self.element_actions.execute_element_action(elements.MIN_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, price)
        # List player on transfer market
        self.element_actions.execute_element_action(elements.LIST_ITEM_ON_TRANSFER_LIST, ElementCallback.CLICK)

    def check_player_price_regular_search(self, player_price):
        searchs = NUMBER_OF_SEARCHS_BEFORE_BINARY_SEARCH
        found_correct_price = False
        for search in range(searchs):
            if int(str(player_price).replace(',', '')) == MIN_PRICE:
                return True, MIN_PRICE
            self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
            time.sleep(1)
            no_results_banner = self.element_actions.get_element(elements.NO_RESULTS_FOUND)
            # check if the player is less than the approximate price or not
            if no_results_banner and found_correct_price:
                self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
                return True, int(str(player_price).replace(',', ''))
            if no_results_banner:
                self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
                self.element_actions.execute_element_action(elements.INCREASE_MAX_PRICE_BTN, ElementCallback.CLICK)
                player_price = self.element_actions.get_element(elements.MAX_BIN_PRICE_INPUT).get_attribute("value")
            if not no_results_banner:
                self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
                # found finally a result save the price and update the flag
                time.sleep(1)
                player_price = self.element_actions.get_element(elements.MAX_BIN_PRICE_INPUT).get_attribute("value")
                found_correct_price = True
                self.element_actions.execute_element_action(elements.DECREASE_MAX_PRICE_BTN, ElementCallback.CLICK)

        return False, player_price

    def get_scale_from_dict(self,upper_bound,lower_bound):
        possible_scales =[]
        for element in MAP_INC_DEC_PRICES.items():
            values = element[0].split("-")
            if upper_bound > int(values[0]) and upper_bound < int(values[1]):
                possible_scales.append(int(element[1]))
            elif lower_bound > int(values[0]) and lower_bound < int(values[1]):
                possible_scales.append(int(element[1]))
        return possible_scales

    def calc_new_max_price(self, down_limit, up_limit, is_inc):
        if is_inc:
            return down_limit + abs(up_limit-down_limit)/2
        else:
            return up_limit - abs(up_limit-down_limit)/2

    def check_player_price_binary_search(self, player_price):
        is_price_raised = False
        # player_last_seen_price = player_price
        # player_new_max_price = player_last_seen_price/2
        # search_scales = self.get_scale_from_dict(player_last_seen_price, player_new_max_price)
        # time.sleep(1)
        # player_new_price_after_webapp_transfer = self.delete_write_click_get_price(self, player_new_max_price)
        # self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
        # time.sleep(2)
        down_limit = MIN_PLAYER_PRICE
        up_limit = int(player_price.replace(',', ''))
        player_new_max_price = self.calc_new_max_price(down_limit, up_limit, 0)
        search_scales = self.get_scale_from_dict(up_limit, down_limit)
        player_price_after_webapp_transfer = self.delete_write_click_get_price(player_new_max_price)
        self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
        while up_limit - down_limit not in search_scales:
            time.sleep(1)
            is_no_results_banner = self.element_actions.get_element(elements.NO_RESULTS_FOUND)
            if is_no_results_banner:
                down_limit = player_price_after_webapp_transfer
                player_new_max_price = self.calc_new_max_price(down_limit, up_limit , 1)
                player_price_after_webapp_transfer = self.delete_write_click_get_price(player_new_max_price)

                search_scales = self.get_scale_from_dict(down_limit, up_limit)
            else:
                up_limit = player_price_after_webapp_transfer
                player_new_max_price = self.calc_new_max_price(down_limit, up_limit, 0)
                player_price_after_webapp_transfer = self.delete_write_click_get_price(player_new_max_price)

                search_scales = self.get_scale_from_dict(down_limit, up_limit)

                # temp_player_new_max_price = player_price_after_webapp_transfer
                # player_new_max_price = self.calc_new_max_price(player_last_max_price,player_new_max_price,0)
                # player_last_max_price = temp_player_new_max_price
                # player_price_after_webapp_transfer = self.delete_write_click_get_price(self, player_new_max_price)
                # search_scales = self.get_scale_from_dict(player_last_max_price, player_new_max_price)
                # found_up_limit = True

            self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
        self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
        return True, up_limit

    def delete_write_click_get_price(self, new_price):

        self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)

        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.CLICK)

        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS,
                                                    Keys.CONTROL, "a")
        time.sleep(0.25)
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, str(new_price))
        time.sleep(0.35)

        self.element_actions.execute_element_action(elements.SEARCH_PRICE_HEADER, ElementCallback.CLICK)

        return int(self.element_actions.get_element(elements.MAX_BIN_PRICE_INPUT).get_attribute("value").replace(',',''))

    def check_player_RT_price(self, player_name, player_revision):
        #found_correct_price = False

        player_futbin_price = get_approximate_min_price(player_name, player_revision)
        #self.element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.CLICK)
        self.element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS,
                                                    Keys.CONTROL, "a")
        time.sleep(0.5)

        self.element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS, player_name)
        self.element_actions.execute_element_action(elements.FIRST_RESULT_INPUT_SEARCH, ElementCallback.CLICK)
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS,
                                                    Keys.CONTROL, "a")
        time.sleep(0.5)
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, str(player_futbin_price))
        find_player_from_regular_search, player_price = self.check_player_price_regular_search(player_futbin_price)
        if find_player_from_regular_search:
            return player_price
        player_price = self.check_if_get_results_in_current_price(player_price)
        find_player_from_binary_search, min_price = self.check_player_price_binary_search(player_price)
        return min_price

    def check_if_get_results_in_current_price(self, player_price):
        self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
        no_results_banner = self.element_actions.get_element(elements.NO_RESULTS_FOUND)
        while(no_results_banner):
            player_price = player_price*2
            player_price = self.delete_write_click_get_price(player_price)
            no_results_banner = self.element_actions.get_element(elements.NO_RESULTS_FOUND)
        return player_price

        # while True:
        #     if int(str(player_price).replace(',','')) == MIN_PRICE:
        #         return MIN_PRICE
        #     self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
        #     time.sleep(1)
        #     no_results_banner = self.element_actions.get_element(elements.NO_RESULTS_FOUND)
        #     # check if the player is less than the approximate price or not
        #     if no_results_banner and found_correct_price:
        #         return int(str(player_price).replace(',',''))
        #     if no_results_banner:
        #         self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
        #         if searchs >= 0:
        #             self.element_actions.execute_element_action(elements.INCREASE_MAX_PRICE_BTN, ElementCallback.CLICK)
        #         else:
        #             self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS,
        #                                                         (player_price/2+((player_price - player_price/2)/2)))
        #
        #
        #         player_price = self.element_actions.get_element(elements.MAX_BIN_PRICE_INPUT).get_attribute("value")
        #     if not no_results_banner:
        #         self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
        #         #found finally a result save the price and update the flag
        #         player_price = self.element_actions.get_element(elements.MAX_BIN_PRICE_INPUT).get_attribute("value")
        #         found_correct_price = True
        #         if searchs >= 0:
        #             self.element_actions.execute_element_action(elements.DECREASE_MAX_PRICE_BTN, ElementCallback.CLICK)
        #             searchs -= 1
        #         else:
        #             self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, player_price/2)