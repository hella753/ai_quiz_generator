from rest_framework import permissions


class IsCreater(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.creator == request.user


class IsThisUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj:
            return True


class CanSeeAnalysis(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user
