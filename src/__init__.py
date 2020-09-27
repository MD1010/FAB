from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from consts import APP_SECRET_KEY, SERVER_IP
from src.routes import register_routes
from utils.helper_functions import server_response

app = Flask(__name__)
app.config['SECRET_KEY'] = APP_SECRET_KEY
JWTManager(app)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['JSON_SORT_KEYS'] = False

def init_app():
    register_routes(app)
    @app.route('/alive',methods=['GET'])
    def test():
        return server_response(alive=True)

    app.run(host=SERVER_IP, debug=True)
