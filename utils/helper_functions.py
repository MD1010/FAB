import json

import bcrypt


def saveToCookiesFile(obj, name):
    with open(name, 'w') as f:
        f.write(json.dumps(obj))


def loadCookiesFile(name):
    with open(name, 'r') as f:
        return json.load(f)


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def jsonify(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
