import re
import logging
from src.utils.logger import logger


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


def test_file_handler_exists():
    """
    Verify that the logger configuration includes a FileHandler writing to 'app.log'.
    """
    file_handlers = [
        handler for handler in logging.getLogger().handlers
        if isinstance(handler, logging.FileHandler)
    ]
    assert any("app.log" in handler.baseFilename for handler in file_handlers), (
        "No FileHandler found that writes to 'app.log'"
    )


def test_logging_to_file(tmp_path):
    """
    Integration test: Temporarily override the FileHandler's filename to a file in a
    temporary directory, log a message, and then verify that the message appears in that file.
    """
    temp_log_file = tmp_path / "test_app.log"

    # Create a new FileHandler with the temporary file
    temp_handler = logging.FileHandler(str(temp_log_file))
    temp_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    temp_handler.setLevel(logging.DEBUG)

    # Get root logger and add temporary handler
    root_logger = logging.getLogger()
    root_logger.addHandler(temp_handler)

    test_message = "Integration test log message"
    logger.debug(test_message)

    # Ensure the log message is written to the temporary log file
    temp_handler.flush()
    with temp_log_file.open("r") as f:
        content = f.read()

    # Clean up by removing the temporary handler
    root_logger.removeHandler(temp_handler)
    temp_handler.close()

    assert test_message in content, "The log message was not found in the temporary log file."
