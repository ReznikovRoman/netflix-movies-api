from .exceptions import ImproperlyConfiguredError


def RequiredAttributes(*required_attrs):  # noqa
    """Метакласс для указания обязательных переменных класса."""
    class RequiredAttributesMeta(type):
        def __init__(cls, name, bases, attrs):
            if not bases:
                return
            if missing_attrs := [attr for attr in required_attrs if not hasattr(cls, attr)]:
                raise ImproperlyConfiguredError(f"{name!r} requires attributes: {missing_attrs}")
    return RequiredAttributesMeta
