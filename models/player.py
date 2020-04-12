from models.Item import Item


class Player(Item):
    def __init__(self, id='', name='', rating='', revision='',  position='', player_image='', club_image='', nation_image=''):
        super().__init__(id, name, type="player")
        self.rating = rating
        self.revision = revision
        self.position = position
        self.profit = 0
        self.market_price = 0
        self.player_image = player_image
        self.club_image = club_image
        self.nation_image = nation_image

    def player_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'rating': self.rating,
            'revision': self.revision,
            'position': self.position,
            'player_image': self.player_image,
            'club_image': self.club_image,
            'nation_image': self.nation_image
        }
