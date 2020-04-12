from models.fab_loop import FabLoop


class ConsumablesLoop(FabLoop):
    def __init__(self, fab, configuration_data, items_with_filters):
        self.fab = fab
        self.configuration_data = configuration_data
        self.items_with_filters = items_with_filters

    def start_loop(self):
        pass
