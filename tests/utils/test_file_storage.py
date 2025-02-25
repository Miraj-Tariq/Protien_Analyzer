import json
import pytest
from pathlib import Path
from src.utils.file_storage import store_data

def test_store_data_json(tmp_path: Path):
    data = {"key": "value"}
    file_path = tmp_path / "test.json"
    stored_path = store_data(data, file_path, format="json")
    assert stored_path.exists()
    with stored_path.open("r") as f:
        loaded = json.load(f)
    assert loaded == data

def test_store_data_invalid_format(tmp_path: Path):
    data = {"key": "value"}
    file_path = tmp_path / "test.txt"
    with pytest.raises(ValueError):
        store_data(data, file_path, format="xml")
