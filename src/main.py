from consts import SERVER_IP
from src.app import app, socketio
from src.api.routes import register_routes

if __name__ == '__main__':
    register_routes()
    socketio.run(app, port=5000, host=SERVER_IP, debug=True)
