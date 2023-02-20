from api.share.responses import ResponseFailure, ResponseSuccess, Response
from api.share.requests import ValidRequestObject


class UseCase:
    def execute(self, request_object: ValidRequestObject) -> Response:
        if not request_object:
            return ResponseFailure.build_from_none_request(self.__class__.__name__)
        try:
            value = self.process_request(request_object)
            return ResponseSuccess(value)
        except Exception as exc:
            return ResponseFailure.build_from_error(self.__class__.__name__, exc)

    def process_request(self, request_object):
        raise NotImplementedError(
            f"process_request() not implemented by {self.__class__.__name__}")
