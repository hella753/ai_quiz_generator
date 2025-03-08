from rest_framework.exceptions import APIException
from rest_framework import status


class DenyTornikeException(APIException):
    """
    Custom exception which is raised when Tornike tries to use the API.
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "თორნიკე აქანე რა გინდა სიმონ ? "
    default_code = "permission_denied"


class QuizGenerationError(Exception):
    """
    Custom exception for quiz generation errors.
    """
    pass
