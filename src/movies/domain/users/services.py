from movies.common.constants import DefaultRoles


class UserService:
    """User service."""

    @staticmethod
    def is_subscriber(roles: list[str]) -> bool:
        """Verify if user has a 'subscriber' role."""
        has_subscription = DefaultRoles.SUBSCRIBERS.value in roles
        return has_subscription
