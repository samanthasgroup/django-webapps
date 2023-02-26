from api.share.requests import ValidRequestObject
from api.share.responses import Response, ResponseFailure, ResponseSuccess


class UseCase:
    """
    Base class for another use cases classes. Inherited classes must implement
    process_request method,     which calls inside the execute method.
    """

    def execute(self, request_object: ValidRequestObject) -> Response:
        if request_object is None:
            return ResponseFailure.build_from_none_request(self.__class__.__name__)
        try:
            value = self.process_request(request_object)
            return ResponseSuccess(value)
        except Exception as exc:
            return ResponseFailure.build_from_error(self.__class__.__name__, exc)

    def process_request(self, request_object):
        raise NotImplementedError(
            f"process_request() not implemented by {self.__class__.__name__}"
        )
