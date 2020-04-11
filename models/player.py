from models.Item import Item


class Player(Item):
    def __init__(self, id='', name='', rating='', revision='', nation='', position='', club='', player_image='', club_image='', nation_image=''):
        super().__init__(id, name, type="player")
        self.rating = rating
        self.revision = revision
        self.position = position
        self.club = club
        self.profit = 0
        self.market_price = 0
        self.nation = nation
        self.player_image = player_image
        self.club_image = club_image
        self.nation_image = nation_image

    def player_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'rating': self.rating,
            'revision': self.revision,
            'nation': self.nation,
            'position': self.position,
            'club': self.club,
            'player_image': self.player_image,
            'club_image': self.club_image,
            'nation_image': self.nation_image
        }
