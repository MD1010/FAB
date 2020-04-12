from abc import ABC, abstractmethod


class SearchFilterSetter(ABC):
    @abstractmethod
    def set_specific_item_name_filter(self, item_name):
        pass

    @abstractmethod
    def set_item_quality_filter(self, item_quality):
        pass

    @abstractmethod
    def set_item_price_filter(self, item_price):
        pass