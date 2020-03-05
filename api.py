from inspect import _empty

import requests
import json

from my_selenium import FabDriver
import server_status_messages

from player_buy import PlayerBuy
from constants import *

from flask import Flask, request, make_response

app = Flask(__name__)
fab_driver = FabDriver()

@app.route('/api/login', methods=['POST'])
def user_login():
    jsonData = request.get_json()
    email = jsonData.get('email')
    password = jsonData.get('password')
    if email is None or password is None:
        return server_status_messages.FAILED_AUTH, 401
    return fab_driver.start_login(email, password)

@app.route('/api/start-fab', methods=['GET'])
def start_fab_loop():
    # my_selenium.start_login(email, password)
    return fab_driver.start_loop()

@app.route('/api/players-list')
def players_list():
    response = requests.get(url=base_players_url)
    players_json = response.json()
    return players_json

@app.route('/api/player/<int:id>')
def player_details(id):
    return 'player details'


@app.route('/api/user-players', methods=['POST', 'GET'])
def user_players():
    if request.method == 'POST':
        jsonData = request.get_json()
        playersSavedList.append(
            PlayerBuy(jsonData['id'], jsonData['name'], jsonData['maxBuyPrice'], jsonData['searchTime'],
                      jsonData['shouldSell']))
        return make_response("", 200)
    if request.method == 'GET':
        return json.dumps(list(map(lambda p: p.player_json(), playersSavedList)))


@app.route('/api/send-status-code', methods=['POST'])
def send_status_code():
    code = request.get_json()['code']
    fab_driver.set_status_code(code)
    #change this nonesense
    return code, 200



if __name__ == '__main__':
    base_players_url = '{0}/{1}/{2}/{3}/{4}/{5}'.format(ROOT_URL, BASE_URL, GUID, YEAR, CONTENT_URL, PLAYERS_JSON)
    playersSavedList = []
    app.run(debug=True)
