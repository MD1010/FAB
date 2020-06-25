import datetime
from typing import List

from models.successful_bid import SuccessfulBid
from models.web_app_auction import WebAppAuction
from src.web_app.player_cards import get_card_attribute_by_def_id
from utils import db


def get_auction_data(auction_info):
    return WebAppAuction(
        auction_info.get('bidState'),
        auction_info.get('startingBid'),
        auction_info.get('buyNowPrice'),
        auction_info.get('currentBid'),
        auction_info.get('expires'),
        auction_info.get('tradeId'),
        auction_info.get('tradeState'))


def sort_results_by_min_bin(auctions: List[WebAppAuction]) -> List[WebAppAuction]:
    return sorted(auctions,key=lambda auction: auction.buy_now_price)


def get_successfull_trade_data(item_data, item_data_from_request):
    if item_data_from_request:
        player_name = item_data_from_request['name']
        rating = item_data_from_request['rating']
        revision = item_data_from_request['revision']
        def_id = item_data_from_request['id']
    # when buying unknown players
    else:
        def_id = item_data.get('resourceId')
        asset_id = item_data.get('assetId')  # base card id - the id we look in the db
        rating = item_data.get('rating')
        player_name = db.players_collection.find_one({'id': asset_id})['name']
        revision = get_card_attribute_by_def_id(player_name, def_id, 'revision')

    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    item_id = item_data.get('id')

    return SuccessfulBid(item_id, def_id, player_name, rating, revision, timestamp)
