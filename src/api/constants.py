import enum


class MESSAGE(str, enum.Enum):
    """Сообщение от сервиса."""

    FILM_NOT_FOUND = "film not found"
    GENRE_NOT_FOUND = "genre not found"
    PERSON_NOT_FOUND = "person not found"
