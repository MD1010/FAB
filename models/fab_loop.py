from abc import ABC, abstractmethod


class FabLoop(ABC):
    @abstractmethod
    def start_loop(self):
        raise NotImplementedError("Method start_loop must be implemented")

