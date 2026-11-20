from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException


class BusinessLogicError(APIException):
    """
    Standard exception for business rule violations in Evently.
    Formats response to:
    {
        "detail": "Human readable message",
        "code": "machine_readable_code"
    }
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Biznes qoidasi buzildi."
    default_code = "business_error"

    def __init__(self, detail=None, code=None, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = detail
        if code is not None:
            self.code = code
        super().__init__(detail=self.detail, code=self.code)


def custom_exception_handler(exc, context):
    """
    Custom exception handler to keep consistent error responses across API.
    """
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(exc, BusinessLogicError):
            response.data = {
                "detail": str(exc.detail),
                "code": getattr(exc, "code", "business_error"),
            }
        elif isinstance(response.data, dict) and "detail" in response.data:
            # If standard DRF error has a code, ensure code is exposed
            code = getattr(exc, "default_code", None)
            if hasattr(exc, "get_codes"):
                codes = exc.get_codes()
                if isinstance(codes, str):
                    code = codes
            if code and "code" not in response.data:
                response.data["code"] = code

    return response
