from consts.app import STATUS_CODE_TRIES


class Fab:
    def __init__(self, driver, element_actions, player_actions, user=None):
        # self.is_authenticated = is_authenticated  # todo remove and handle all the places that is_autheticated needed.add function that checks if the user is in the active list
        self.driver = driver
        self.element_actions = element_actions
        self.player_actions = player_actions
        self.user = user
        # self.player_actions = None
        # self.driver_state = DriverState.OFF
        # self.connected_user_details = {}
        self.time_left_to_run = 0

        self.user_coin_balance = 0

        self.coins_earned = 0
        self.runtime = 0

    def initialize_fab(self, driver):
        self.driver = driver

