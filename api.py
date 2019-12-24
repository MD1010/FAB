import requests
import json

import my_selenium

from player_buy import PlayerBuy
from constants import *

from flask import Flask, request, make_response
app = Flask(__name__)

@app.route('/api/login', methods = ['GET'])
def user_login():
    my_selenium.start_login()
    return 'ok'

@app.route('/api/players-list')
def players_list():
    response = requests.get(url = base_players_url)
    players_json = response.json()
    return players_json

@app.route('/api/player/<int:id>')
def player_details(id):
    return 'player details'

@app.route('/api/user-players', methods = ['POST', 'GET'])
def user_players():
    if request.method == 'POST':
        jsonData = request.get_json()
        playersSavedList.append(PlayerBuy(jsonData['id'], jsonData['name'], jsonData['maxBuyPrice'], jsonData['searchTime'], jsonData['shouldSell']))
        return make_response("", 200)
    if request.method == 'GET':
        return json.dumps(list(map(lambda p: p.player_json(), playersSavedList)))

if __name__ == '__main__':
    base_players_url = '{0}/{1}/{2}/{3}/{4}/{5}'.format(ROOT_URL, BASE_URL, GUID, YEAR, CONTENT_URL, PLAYERS_JSON)
    playersSavedList = []
    app.run()