import re
import logging
from src.utils.logger import get_logger

logger = get_logger(__name__)

def test_logger_name():
    assert logger.name == __name__

def test_logger_instance():
    """
    Verify that the centralized logger is an instance of logging.Logger.
    """
    assert isinstance(logger, logging.Logger), "Logger is not an instance of logging.Logger"


def test_logger_level():
    """
    Verify that the root logger level is set to DEBUG as configured.
    """
    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG, "Root logger level is not DEBUG"


def test_logging_output_format(caplog):
    """
    Capture log output using pytest's caplog fixture and verify that the
    log messages follow the expected format:
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    """
    test_message = "Test info message"
    with caplog.at_level(logging.INFO):
        logger.info(test_message)

    # The expected format includes a timestamp, log level, logger name, and message.
    # We'll use a regular expression to verify the structure.
    pattern = r"\d{4}-\d{2}-\d{2}.*\s+\[INFO\]\s+.+: " + re.escape(test_message)
    matches = [line for line in caplog.text.splitlines() if re.search(pattern, line)]
    assert matches, f"Log output did not match expected format. Output was: {caplog.text}"
