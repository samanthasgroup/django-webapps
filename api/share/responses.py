from abc import ABC


class Response(ABC):
    pass


class ResponseSuccess(Response):

    def __init__(self, value=None):
        self.value = value

    def __bool__(self):
        return True


class ResponseFailure(Response):

    def __init__(self, errors):
        self.errors = errors

    @property
    def value(self):
        return self.errors

    def __bool__(self):
        return False

    @classmethod
    def build_from_none_request(cls, use_case_name: str):
        errors = [f"No request in {use_case_name}"]
        return cls(errors)

    @classmethod
    def build_from_error(cls, object_name: str, exc: Exception):
        errors = [f"{str(exc)} in {object_name}"]
        return cls(errors)