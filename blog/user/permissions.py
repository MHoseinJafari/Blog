from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    message = "you ate not owner of this post."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the blog.
        return obj.author == request.user