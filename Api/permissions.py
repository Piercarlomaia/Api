from rest_framework import permissions

class IsUserPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.email == request.user

class IsChavesPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.fkuser == request.user