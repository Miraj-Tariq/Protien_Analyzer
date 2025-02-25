from src.utils.logger import get_logger

def test_logger_name():
    logger = get_logger(__name__)
    assert logger.name == __name__
