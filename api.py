import requests
import json

from main import Fab
from consts import server_status_messages

from players.models.player import Player
from consts.app import *


from flask import Flask, request, make_response

from players.player_buy import get_current_player_min_price

app = Flask(__name__)
fab_driver = Fab()


@app.route('/api/login', methods=['POST'])
def user_login():
    jsonData = request.get_json()
    email = jsonData.get('email')
    password = jsonData.get('password')
    if email is None or password is None:
        return server_status_messages.BAD_REQUEST, 400
    return fab_driver.start_login(email, password)


@app.route('/api/start-fab', methods=['POST'])
def start_fab_loop():
    # my_selenium.start_login(email, password)
    jsonData = request.get_json()
    time_to_run = jsonData.get('time')
    if time_to_run is None:
        return server_status_messages.BAD_REQUEST, 400
    return fab_driver.start_loop(time_to_run)


@app.route('/api/players-list')
def players_list():
    response = requests.get(url=base_players_url)
    players_json = response.json()
    return players_json

@app.route('/api/user-players', methods=['POST', 'GET'])
#fix this
def user_players():
    if request.method == 'POST':
        # jsonData = request.get_json()
        # playersSavedList.append(
        #     Player(jsonData['id'], jsonData['name'], jsonData['maxBuyPrice'], jsonData['searchTime'],jsonData['shouldSell']))
        # return make_response("", 200)
        pass
    if request.method == 'GET':
        return json.dumps(list(map(lambda p: p.player_json(), playersSavedList)))

@app.route('/jenia-test')
def player_details():
    return get_current_player_min_price('Clément Lenglet', 'NIF')

@app.route('/api/send-status-code', methods=['POST'])
def send_status_code():
    code = request.get_json()['code']
    fab_driver.set_status_code(code)
    return (server_status_messages.SUCCESS_AUTH, 200) if fab_driver.is_authenticated else (server_status_messages.FAILED_AUTH, 401)


if __name__ == '__main__':
    base_players_url = '{0}/{1}/{2}/{3}/{4}/{5}'.format(ROOT_URL, BASE_URL, GUID, YEAR, CONTENT_URL, PLAYERS_JSON)
    playersSavedList = []
    app.run(debug=True)
