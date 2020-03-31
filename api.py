import datetime
import json

import requests
from flask import Flask, request, Response, jsonify
from flask_jwt_extended import jwt_required, JWTManager, create_access_token

from auth.login import set_status_code
from auth.signup import sign_up
from consts import server_status_messages
from consts.app import *
from main import Fab
from players.player_search import get_all_players_cards
from utils.driver import close_driver

app = Flask(__name__)
app.config['SECRET_KEY'] = APP_SECRET_KEY

jwt = JWTManager(app)
fab_driver = Fab()


@app.route('/api/login', methods=['POST'])
def user_login():
    # apend new fab to fab_list

    jsonData = request.get_json()
    email = jsonData.get('email')
    password = jsonData.get('password')
    response_obj = fab_driver.start_login(email, password)
    return response_obj


@app.route('/api/start-fab', methods=['POST'])
@jwt_required
def start_fab_loop():
    jsonData = request.get_json()
    time_to_run = jsonData.get('time')
    requested_players = jsonData.get('requested_players')
    return fab_driver.start_fab(time_to_run, requested_players)


@app.route('/api/players-list/<string:searched_player>', methods=['GET'])
# @jwt_required
def get_all_cards(searched_player):
    result = get_all_players_cards(searched_player)
    return Response(json.dumps(list(map(lambda p: p.player_json(), result))),mimetype="application/json")
    # return Response(response=response_obj, mimetype="application/json")


@app.route('/api/send-status-code', methods=['POST'])
@jwt_required
def send_status_code():
    code = request.get_json()['code']
    return set_status_code(fab_driver, code)
    # return Response(response=response_obj, mimetype="application/json")


@app.route("/api/close-driver")
# @jwt_required
def close_running_driver():
    return close_driver(fab_driver)


@app.route("/api/driver-state")
@jwt_required
def check_driver_state():
    return jsonify(state=fab_driver.driver_state.value)


@app.route("/api/signup", methods=['POST'])
def sign_up_user():
    jsonData = request.get_json()
    email = jsonData.get('email')
    password = jsonData.get('password')
    if email is None or password is None:
        return server_status_messages.BAD_REQUEST, 400
    return sign_up(email, password)


if __name__ == '__main__':
    base_players_url = '{0}/{1}/{2}/{3}/{4}/{5}'.format(ROOT_URL, BASE_URL, GUID, YEAR, CONTENT_URL, PLAYERS_JSON)
    app.run(debug=True)
