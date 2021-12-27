from jsonschema import validate


class Validator:
    type_data = None
    type_registry = {}

    def __init_subclass__(cls, **kwargs):
        cls.type_registry[cls.type_data] = cls

    def __init__(self, event, data):
        self.schema = event.validators
        self.data = data

    def validate(self):
        return ["Not implemented"]

    @classmethod
    def get_validator(cls, event, data):
        registry = cls.type_registry.get(
            event.validators.__class__.__name__, Validator
        )
        return registry(event, data)


class ValidatorDict(Validator):
    type_data = dict.__name__

    def validate(self):
        try:
            validate(self.data, self.schema)
        except Exception as e:
            return [str(e.message)]
        return []


class ValidatorList(Validator):
    type_data = list.__name__

    def validate(self):
        response = []
        for schema in self.schema:
            try:
                validate(self.data, schema)
                return []
            except Exception as e:
                response.append(e.message)
        return response
