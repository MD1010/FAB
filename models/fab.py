import time


class Fab:
    def __init__(self, driver, element_actions, item_actions, ea_account=None):
        self.driver = driver
        self.element_actions = element_actions
        self.item_actions = item_actions
        self.ea_account = ea_account
        self.time_left_to_run = 0
        self.runtime = 0
        self.driver_crashes = 0
        self.start_runtime = time.time()
