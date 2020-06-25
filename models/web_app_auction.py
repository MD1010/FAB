class WebAppAuction:
    def __init__(self, bid_state, starting_bid, buy_now_price, current_bid, expires, trade_id, trade_state):
        self.bid_state = bid_state
        self.starting_bid = starting_bid
        self.buy_now_price = buy_now_price
        self.current_bid = current_bid
        self.expires = expires
        self.trade_id = trade_id
        self.trade_state = trade_state
