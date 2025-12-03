import logging

LOG_MARKER = "[MARKER]"


class MarkerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return f"{LOG_MARKER} {msg}", kwargs


def get_logger(name: str = "user_display") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt=f"%(asctime)s {LOG_MARKER} %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = True
    return MarkerAdapter(logger, {})


def log_exception(logger: logging.Logger, msg: str, exc: Exception) -> None:
    logger.exception(f"{msg}: {exc}")
