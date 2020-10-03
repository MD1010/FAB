from consts import SERVER_IP
from src.app import app, socketio

print("OUT")
if __name__ == '__main__':
    from src.api.routes import register_routes
    print("IN")
    register_routes()

    socketio.run(app, port=5000, host=SERVER_IP, debug=True)
