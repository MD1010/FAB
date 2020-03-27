import requests
import json

from auth.login import set_status_code
from auth.signup import sign_up
from driver import close_driver
from main import Fab
from consts import server_status_messages

from consts.app import *

from flask import Flask, request, Response

from players.player_search import get_all_players_cards
from server_status import ServerStatus

app = Flask(__name__)
fab_driver = Fab()


@app.route('/api/login', methods=['POST'])
def user_login():
    jsonData = request.get_json()
    email = jsonData.get('email')
    password = jsonData.get('password')
    response_obj = fab_driver.start_login(email, password)
    return Response(response=response_obj, mimetype="application/json")


@app.route('/api/start-fab', methods=['POST'])
def start_fab_loop():
    jsonData = request.get_json()
    time_to_run = jsonData.get('time')
    requested_players = jsonData.get('requested_players')
    response_obj = fab_driver.start_loop(time_to_run, requested_players)
    return Response(response=response_obj, mimetype="application/json")



@app.route('/api/players-list')
def players_list():
    response = requests.get(url=base_players_url)
    players_json = response.json()
    return Response(response=players_json, mimetype="application/json")


@app.route('/api/players-list/<string:searched_player>', methods=['GET'])
def get_all_cards(searched_player):
    result = get_all_players_cards(searched_player)
    response_obj = json.dumps(list(map(lambda p: p.player_json(), result)))
    return Response(response=response_obj, mimetype="application/json")


@app.route('/api/send-status-code', methods=['POST'])
def send_status_code():
    code = request.get_json()['code']
    set_status_code(fab_driver,code)
    response_obj = ServerStatus(server_status_messages.SUCCESS_AUTH, 200).jsonify() \
        if fab_driver.is_authenticated \
        else ServerStatus(server_status_messages.FAILED_AUTH, 401).jsonify()
    return Response(response=response_obj, mimetype="application/json")


@app.route("/api/close-driver")
def close_running_driver():
    response_obj = close_driver(fab_driver)
    return Response(response=response_obj, mimetype="application/json")


@app.route("/api/driver-state")
def check_driver_state():
    return {'state': fab_driver.driver_state.value}


@app.route("/api/signup", methods=['POST'])
def sign_up_user():
    jsonData = request.get_json()
    email = jsonData.get('email')
    password = jsonData.get('password')
    if email is None or password is None:
        return server_status_messages.BAD_REQUEST, 400
    response_obj = sign_up(email, password)
    return Response(response=response_obj, mimetype="application/json")


if __name__ == '__main__':
    base_players_url = '{0}/{1}/{2}/{3}/{4}/{5}'.format(ROOT_URL, BASE_URL, GUID, YEAR, CONTENT_URL, PLAYERS_JSON)
    app.run(debug=True)
