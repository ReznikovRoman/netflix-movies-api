from movies.common.constants import DefaultRoles


class UserService:
    """Сервис для работы с пользователями."""

    @staticmethod
    def is_subscriber(roles: list[str]) -> bool:
        """Проверка ролей пользователя на 'Подписчика'."""
        has_subscription = DefaultRoles.SUBSCRIBERS.value in roles
        return has_subscription
