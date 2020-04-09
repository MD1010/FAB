class Fab:
    def __init__(self, driver, element_actions, player_actions, user=None):
        self.driver = driver
        self.element_actions = element_actions
        self.player_actions = player_actions
        self.user = user
        self.time_left_to_run = 0
        self.coins_earned = 0
        self.runtime = 0
        self.driver_crashes = 0
