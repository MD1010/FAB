from flask import Blueprint


class NestedBlueprint(Blueprint):
    def __init__(self, parent_blueprint, prefix):
        super(NestedBlueprint, self).__init__(prefix, prefix)
        self.blueprint = parent_blueprint
        self.prefix = '/' + prefix

    def route(self, path, **options):
        path = self.prefix + path
        return self.blueprint.route(path, **options)
