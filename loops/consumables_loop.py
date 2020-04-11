from loops.fab_loop import FabLoop


class ConsumablesLoop(FabLoop):
    def start_loop(self, fab, configuration_data, requested_players, user_prices, filters=None):
        if filters is None:
            filters = []