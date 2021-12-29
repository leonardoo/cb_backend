from jsonschema import validate


class Validator:
    """
    Class that handle all the validations from the diffents schema in the event definition
    """
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
        """
        Get the validator according to the type of the event definition, if this definition dont exists
        will return the base class
        """
        registry = cls.type_registry.get(
            event.validators.__class__.__name__, Validator
        )
        return registry(event, data)


class ValidatorDict(Validator):
    """
    Class that handle the validations when the schema is a dict and assume that is only one
    schema
    """
    type_data = dict.__name__

    def validate(self):
        """
        Validate the data with the schema, if there is no valid, will return error message inside a list
        else will return an empty list
        """
        try:
            validate(self.data, self.schema)
        except Exception as e:
            return [str(e.message)]
        return []


class ValidatorList(Validator):
    """
    Class that handle a schema when this has multiple schemas, so we can have a complete list of validations
    """
    type_data = list.__name__

    def validate(self):
        """
        Validate the data with the schema, if there is no valid, will return all the errors by schema
        else will return an empty list
        """
        response = []
        for schema in self.schema:
            try:
                validate(self.data, schema)
                return []
            except Exception as e:
                response.append(e.message)
        return response
