# from enums.item_types import ItemTypes
# from search_filters.consumables_filters import ConsumablesFilteredSearch
# from search_filters.filtered_search_by_name import FilteredSearch
#
#
# class FilterSearchFactory:
#     def __init__(self, item, player_custom_filters=None):
#         self.item = item
#         self.player_custom_filters = player_custom_filters
#
#     def get_filter_search_object(self):
#         if ItemTypes.PLAYER == ItemTypes(self.item.type):
#            return Filtered
#         return ConsumablesFilteredSearch()
