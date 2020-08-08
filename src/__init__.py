import pychrome as pychrome
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.driver import ChromeDriver

from consts import APP_SECRET_KEY, SERVER_IP
from src.routes import register_routes
from utils.helper_functions import server_response

app = Flask(__name__)
app.config['SECRET_KEY'] = APP_SECRET_KEY
JWTManager(app)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['JSON_SORT_KEYS'] = False
messages = []


def init_app():
    register_routes(app)

    @app.route('/alive',methods=['GET'])
    def test():
        return server_response(alive=True)

    # @app.route("/stream")
    # def stream():
    #     def event_stream():
    #         # while True:
    #             if len(messages) > 0:
    #                 message = messages.pop(0)
    #                 return f"data:{message}\nevent:myEvent\n\n"
    #     return Response(event_stream(), mimetype="text/event-stream")
    app.run(host=SERVER_IP, debug=True)
