import logging

from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import ValidationError, PermissionDenied, NotAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class ErrorHandlingMixin:
    """
    Mixin to provide consistent error handling across ViewSets.
    """
    def handle_exception(self, exc):
        """
        Handle exceptions consistently across all ViewSets.
        """
        if isinstance(exc, ValidationError):
            logger.error(f"Validation error: {str(exc)}", exc_info=True)
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, IntegrityError):
            logger.error(f"Integrity error: {str(exc)}", exc_info=True)
            error_message = str(exc)
            if "foreign key constraint" in error_message:
                return Response(
                    {"error": "Referenced entity does not exist"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {"error": "Database integrity error"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif isinstance(exc, PermissionDenied):
            logger.error(f"Permission denied: {str(exc)}", exc_info=True)
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )
        elif isinstance(exc, NotAuthenticated):
            logger.error(f"Not authenticated: {str(exc)}", exc_info=True)
            return Response(
                {"error": "Cannot use this feature if you are not authenticated"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        else:
            logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
