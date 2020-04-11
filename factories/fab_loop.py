from loops.consumables_loop import ConsumablesLoop
from loops.filtered_player_loop import FilteredPlayerLoop
from loops.player_loop_by_name import NameFilteredPlayerLoop


class FabLoopFactory:
    def __init__(self, loop_type):
        self.loop_type = loop_type

    def get_fab_loop(self):
        fab_loops = {
            "playerNames": NameFilteredPlayerLoop(),
            "customFilters": FilteredPlayerLoop(),
            "consumables": ConsumablesLoop()
        }
        return fab_loops[self.loop_type]
