import logging
import sys
import webbrowser

from loguru import logger


def open_browser() -> None:
    webbrowser.open("http://localhost:1234")


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_loguru_intercept():
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Intercept logs from the 'requests' library
    requests_logger = logging.getLogger("requests")
    requests_logger.handlers = [InterceptHandler()]
    requests_logger.propagate = False

    # Configure Loguru
    logger.remove()  # Remove default handler
    # logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
    logger.add(sys.stderr, level="INFO")
    # logger.add("file.log", rotation="10 MB")


# Call the setup function immediately
setup_loguru_intercept()
