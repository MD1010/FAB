from models.search_filter_setter import SearchFilterSetter


class ConsumablesSearchFilterSetter(SearchFilterSetter):
    def __init__(self, element_actions):
        self.element_actions = element_actions

    def set_item_quality_filter(self, consumable_quality):
        pass

    def set_specific_item_name_filter(self, consumable_name):
        pass

    def set_item_price_filter(self, consumable_price):
        pass
