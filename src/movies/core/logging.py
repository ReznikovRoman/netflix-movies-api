import logging


async def configure_logger() -> None:
    """Configure built-in logger."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
    )
