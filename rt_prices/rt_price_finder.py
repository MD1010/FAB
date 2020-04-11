from abc import ABC, abstractmethod


class FutbinPriceFinder(ABC):
    @abstractmethod
    def get_futbin_price(self, item, user_email):
        raise NotImplementedError("Method init_market_search must be implemented")
