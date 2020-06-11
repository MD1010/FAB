from flask import Blueprint

from utils.nested_blueprint import NestedBlueprint

webapp = Blueprint("webapp", __name__)

login = NestedBlueprint(webapp, 'login')
actions = NestedBlueprint(webapp, 'actions')



