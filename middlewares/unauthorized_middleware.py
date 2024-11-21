from django.utils.deprecation import MiddlewareMixin
import uuid


class AnonymousUserMiddleware(MiddlewareMixin):
    """
    Processes the request. sets the name of the guest users
    """
    def process_request(self, request):
        user = request.user
        if user.is_anonymous:
            if "guest_user_name" not in request.session:
                unique_id = uuid.uuid4()
                request.session["guest_user_name"] = f"Guest-{unique_id}"
            user.name = request.session["guest_user_name"]
