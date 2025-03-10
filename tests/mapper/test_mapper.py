import json
import pytest
from pathlib import Path
from src.mapper.mapper import Mapper

@pytest.fixture
def sample_mapping_file(tmp_path: Path) -> Path:
    """
    Creates a temporary mapping JSON file for testing.
    """
    data = {
        "MET": "M",
        "ALA": "A",
        "GLY": "G"
    }
    mapping_file = tmp_path / "amino_acids_mapping.json"
    with mapping_file.open("w") as f:
        json.dump(data, f)
    return mapping_file

def test_load_mapping(sample_mapping_file: Path):
    """
    Test that the mapper loads the mapping file correctly.
    """
    mapper = Mapper(str(sample_mapping_file))
    assert mapper.mapping == {"MET": "M", "ALA": "A", "GLY": "G"}

def test_one_to_one_mapping_all_valid(sample_mapping_file: Path):
    """
    Test mapping a dictionary where all codes exist in the mapping.
    """
    mapper = Mapper(str(sample_mapping_file))
    sequences = {
        "H": ["MET", "ALA"],
        "L": ["GLY", "MET"]
    }
    mapped = mapper.one_to_one_mapping(sequences)
    expected = {
        "H": ["M", "A"],
        "L": ["G", "M"]
    }
    assert mapped == expected

def test_one_to_one_mapping_with_missing(sample_mapping_file: Path, caplog):
    """
    Test mapping a dictionary containing an unknown code. The unknown code should be replaced with "X"
    and a warning should be logged.
    """
    mapper = Mapper(str(sample_mapping_file))
    sequences = {
        "H": ["MET", "XYZ"],
        "L": ["ALA"]
    }
    mapped = mapper.one_to_one_mapping(sequences)
    expected = {
        "H": ["M", "X"],
        "L": ["A"]
    }
    assert mapped == expected
    # Check that a warning was logged for the missing mapping.
    assert "Mapping for residue 'XYZ' not found" in caplog.text
