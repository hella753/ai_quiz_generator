from rest_framework.views import exception_handler
from .custom_exceptions import DanyTornikeException


def custom_exception_handler(exc, context):
    """
    This function is responsible for handling custom exceptions.
    """
    response = exception_handler(exc, context)

    if isinstance(exc, DanyTornikeException):
        response.data = {
            'error': exc.default_detail,
            'status_code': exc.status_code,
        }
    return response
