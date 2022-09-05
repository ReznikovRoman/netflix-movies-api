import logging


async def configure_logger() -> None:
    """Базовая настройка встроенного логгера."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
    )
