from rest_framework import permissions
import re


class IsCreater(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.creator == request.user


class DenyAllForTornike(permissions.BasePermission):
   
    def normalize_username(self, username):
        normalized_username = re.sub(r'[^a-zA-Z]', '', username).lower()
        return normalized_username

    def has_permission(self, request, view):
        normalized_username = self.normalize_username(request.user.username)
        return normalized_username != "tornike"

    def has_object_permission(self, request, view, obj):
        normalized_username = self.normalize_username(request.user.username)
        return normalized_username != "tornike"