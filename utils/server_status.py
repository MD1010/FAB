import json


class ServerStatus:
    def __init__(self, message, code):
        self.message = message
        self.code = code

    def jsonify(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
