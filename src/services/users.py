from common.constants import DefaultRoles


class UserService:
    """Сервис для работы с пользователями."""

    @staticmethod
    def is_subscriber(roles: list[str]) -> bool:
        has_subscription = DefaultRoles.SUBSCRIBERS.value in roles
        return has_subscription
