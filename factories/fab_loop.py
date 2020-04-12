from loops.consumables_loop import ConsumablesLoop
from loops.players_loop import PlayerLoop


class FabLoopFactory:
    def __init__(self, loop_type, fab, configuration_data, search_options):
        self.loop_type = loop_type
        self.fab = fab
        self.configuration_data = configuration_data
        self.search_options = search_options

    def get_fab_loop(self):
        fab_loops = {
            "players": PlayerLoop(self.fab, self.configuration_data, self.search_options),
            "consumables": ConsumablesLoop(self.fab, self.configuration_data, self.search_options)
        }
        return fab_loops[self.loop_type]
