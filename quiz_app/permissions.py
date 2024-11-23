from rest_framework import permissions


class IsCreater(permissions.BasePermission):
    """
    Custom permission to only allow creators of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.creator == request.user


class IsThisUser(permissions.BasePermission):
    """
    Custom permission to only allow users to see their own data.
    """
    def has_object_permission(self, request, view, obj):
        if request.user == obj:
            return True


class CanSeeAnalysis(permissions.BasePermission):
    """
    Custom permission to only allow users to see analysis of their own quiz.
    """
    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user
