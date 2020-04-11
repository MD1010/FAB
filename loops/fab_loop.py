from abc import ABC, abstractmethod


class FabLoop(ABC):
    @abstractmethod
    def start_loop(self, fab, configuration_data, requested_players, user_prices, filters=None):
        raise NotImplementedError("Method start_loop must be implemented")

