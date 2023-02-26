from api.share.requests import InvalidRequestObject, ValidRequestObject


class GetAssessmentTestsRequest(ValidRequestObject):
    available_lang = ["en"]

    def __init__(self, language: str, level: str):
        self.language = language
        self.level = level

    @classmethod
    def from_dict(cls, input_dict):
        # Check input parameters.
        invalid_request = InvalidRequestObject()

        if (
            input_dict.get("language")
            and input_dict.get("language") not in GetAssessmentTestsRequest.available_lang
        ):
            invalid_request.add_error("language", "Incorrect value")

        if invalid_request.has_errors():
            return invalid_request

        return cls(language=input_dict.get("language"), level=input_dict.get("level"))
