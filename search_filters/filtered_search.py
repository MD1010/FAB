from abc import ABC, abstractmethod


class FilteredSearch(ABC):
    @abstractmethod
    def set_search_filteres(self,element_actions, item, custom_filters=None):
        raise NotImplementedError("Method set_search_filteres must be implemented")