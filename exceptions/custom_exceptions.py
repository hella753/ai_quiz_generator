from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext_lazy as _


class DenyTornikeException(APIException):
    """
    Custom exception which is raised when Tornike tries to use the API.
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _("თორნიკე აქანე რა გინდა სიმონ ? ")
    default_code = "permission_denied"
