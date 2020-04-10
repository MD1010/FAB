from abc import abstractmethod, ABC


class MarketSearch(ABC):

    @abstractmethod
    def init_market_search(self, filters, price):
        raise NotImplementedError("Method init_market_search must be implemented")
