from abc import ABC, abstractmethod


class FabLoop(ABC):
    @abstractmethod
    def start_loop(self, fab, configuration_data, requested_players, user_prices):
        raise NotImplementedError("Method init_market_search must be implemented")
