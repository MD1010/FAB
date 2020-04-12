from models.fab_loop import FabLoop


class ConsumablesLoop(FabLoop):
    def __init__(self, fab, configuration_data, search_options):
        self.fab = fab
        self.configuration_data = configuration_data
        self.search_options = search_options

    def start_loop(self):
        pass
