from abc import ABC, abstractmethod


class FabLoop(ABC):
    @abstractmethod
    def start_loop(self, fab, configuration_data, items_with_filteres):
        raise NotImplementedError("Method start_loop must be implemented")

