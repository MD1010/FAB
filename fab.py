from consts.app import STATUS_CODE_TRIES


class Fab:
    def __init__(self, driver, is_authenticated=False):
        self.is_authenticated = is_authenticated  # todo remove and handle all the places that is_autheticated needed.add function that checks if the user is in the active list
        self.driver = driver
        # elf.element_actions = None
        # self.player_actions = None
        # self.driver_state = DriverState.OFF
        # self.connected_user_details = {}
        self.time_left_to_run = 0
        self.tries_with_status_code = STATUS_CODE_TRIES
        # self.coin_balance = 0 todo do function that get the current coin balance.
        self.coins_earned = 0
        self.runtime = 0

    def initialize_fab(self,driver):
        self.driver = driver
        self.is_authenticated = True
