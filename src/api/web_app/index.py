from flask import Blueprint

from utils.nested_blueprint import NestedBlueprint

web_app = Blueprint("web_app", __name__)

login = NestedBlueprint(web_app, 'login')
actions = NestedBlueprint(web_app, 'actions')
entities = NestedBlueprint(web_app, 'entities')

