from abc import abstractmethod, ABC


class MarketSearch(ABC):

    @abstractmethod
    def set_name_and_price_filters(self, filters, price):
        raise NotImplementedError("Method init_market_search must be implemented")
