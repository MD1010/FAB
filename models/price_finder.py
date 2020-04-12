from abc import ABC, abstractmethod


class FutbinPriceFinder(ABC):
    @abstractmethod
    def get_futbin_price(self):
        raise NotImplementedError("Method get_futbin_price must be implemented")
