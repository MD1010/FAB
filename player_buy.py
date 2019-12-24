class PlayerBuy:
    def __init__(self, id, name, maxBuyPrice, searchTime, shouldSell):
        self.id = id
        self.name = name
        self.maxBuyPrice = 0
        self.searchTime = 0
        self.shouldSell = False

    def player_json(self):
        return {
            'id' : self.id, 
            'name' : self.name,
            'maxBuyPrice' : self.maxBuyPrice,
            'searcTime' : self.searchTime,
            'shouldSell' : self.shouldSell
        }