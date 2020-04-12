from loops.consumables_loop import ConsumablesLoop
from loops.player_loop import PlayerLoop


class FabLoopFactory:
    def __init__(self, loop_type, fab, configuration_data, items_with_filters):
        self.loop_type = loop_type
        self.fab = fab
        self.configuration_data = configuration_data
        self.items_with_filters = items_with_filters

    def get_fab_loop(self):
        fab_loops = {
            "players": PlayerLoop(self.fab, self.configuration_data, self.items_with_filters),
            "consumables": ConsumablesLoop(self.fab, self.configuration_data, self.items_with_filters)
        }
        return fab_loops[self.loop_type]
