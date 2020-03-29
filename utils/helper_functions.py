import json

def saveToCookiesFile(obj, name):
    with open(name, 'w') as f:
        f.write(json.dumps(obj))


def loadCookiesFile(name):
    with open(name, 'r') as f:
        return json.load(f)
