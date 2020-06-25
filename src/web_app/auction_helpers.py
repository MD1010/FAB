from typing import List

from models.web_app_auction import WebAppAuction


def get_auction_data(item_data):
    return WebAppAuction(
        item_data.get('bidState'),
        item_data.get('startingBid'),
        item_data.get('buyNowPrice'),
        item_data.get('currentBid'),
        item_data.get('expires'),
        item_data.get('tradeId'),
        item_data.get('tradeState'))


def get_auction_with_min_bin(auctions: List[WebAppAuction]):
    return min(auctions, key=lambda auction: auction.buy_now_price)


def notify_successfull_trade_data(def_id):
    pass