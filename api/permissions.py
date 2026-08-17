from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):

    message = "Admin access required."

    def has_permission(
        self,
        request,
        view
    ):
        return (
            request.user.is_authenticated
            and request.user.is_admin()
        )


class IsOwnerOrAdmin(BasePermission):

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):

        if (
            request.user.is_authenticated
            and request.user.is_admin()
        ):
            return True

        owner = getattr(
            obj,
            "author",
            None
        )

        if owner is None:
            owner = getattr(
                obj,
                "user",
                None
            )

        return owner == request.user