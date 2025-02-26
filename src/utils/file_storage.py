import json
from pathlib import Path
from typing import Any, Union
from src.utils.logger import get_logger

logger = get_logger(__name__)


def store_data(data: Any, file_path: Union[str, Path], format: str = "json", **kwargs) -> Path:
    """
    Generic utility to store data in a specified format.

    Args:
        data (Any): The data to be stored.
        file_path (Union[str, Path]): The destination file path.
        format (str): The format to store data ("json" supported by default).
        **kwargs: Additional parameters for the writer.

    Returns:
        Path: The Path object of the stored file.
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if format.lower() == "json":
        try:
            with file_path.open("w") as f:
                json.dump(data, f, indent=4, **kwargs)
            logger.info(f"Data stored as JSON at {file_path.resolve()}")
        except Exception as e:
            logger.error(f"Error storing JSON data: {e}")
            raise e
    else:
        raise ValueError(f"Unsupported format: {format}")

    return file_path
