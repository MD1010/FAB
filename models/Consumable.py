from models.Item import Item


class Consumable(Item):
    def __init__(self, id='',name=''):
        super().__init__(id, name)
