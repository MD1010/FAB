from enums.item_types import ItemTypes
from search_filters.set_consumables_search_filters import ConsumablesSearchFilterSetter
from search_filters.set_player_search_filteres import PlayerSearchFilterSetter


class FiltersSetterFactory:
    def __init__(self, item, element_actions):
        self.item = item
        self.element_actions = element_actions

    def get_filters_setter_object(self):
        if ItemTypes(self.item.type) == ItemTypes.PLAYER:
           return PlayerSearchFilterSetter(self.element_actions)
        if ItemTypes(self.item.type) == ItemTypes.CHEMISTRY_STYLE:
            return ConsumablesSearchFilterSetter(self.element_actions)
        #add more options