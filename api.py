import requests
import json

from main import Fab
from consts import server_status_messages

from consts.app import *

from flask import Flask, request

from players.player_search import get_type_results
from bson import json_util

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
    requested_players = jsonData.get('requested_players')
    if time_to_run is None:
        return server_status_messages.BAD_REQUEST, 400
    return fab_driver.start_loop(time_to_run, requested_players)


@app.route('/api/players-list')
def players_list():
    response = requests.get(url=base_players_url)
    players_json = response.json()
    return players_json


@app.route('/api/players-list/<string:searched_player>', methods=['GET'])
def get_all_cards(searched_player):
    response = requests.get(url=base_players_url)
    ea_players_json = response.json()
    result = get_type_results(searched_player)
    return {"found":json.loads(json_util.dumps(result))}
    # return json.dumps(list(map(lambda p: p.player_json(), result)))
    # ea_players_json = json.dumps(list(map(lambda p: p.player_json(), playersSavedList)))
    # return fab_driver.get_all_players_full_data(ea_players_json)
    # return json.dumps(list(map(lambda p: p.player_json(), playersSavedList)))


@app.route('/api/send-status-code', methods=['POST'])
def send_status_code():
    code = request.get_json()['code']
    fab_driver.set_status_code(code)
    return (server_status_messages.SUCCESS_AUTH, 200) if fab_driver.is_authenticated else (server_status_messages.FAILED_AUTH, 401)


if __name__ == '__main__':
    base_players_url = '{0}/{1}/{2}/{3}/{4}/{5}'.format(ROOT_URL, BASE_URL, GUID, YEAR, CONTENT_URL, PLAYERS_JSON)
    app.run(debug=True)
