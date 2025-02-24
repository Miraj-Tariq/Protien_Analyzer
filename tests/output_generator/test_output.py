import json
import os
from pathlib import Path
from datetime import datetime
import pytest
from src.output_generator.output import OutputFileGenerator

@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """
    Creates a temporary directory to simulate the output directory.
    """
    output_dir = tmp_path / "data" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

@pytest.fixture
def sample_extracted_chains() -> dict:
    """
    Provides a sample extracted_chains dictionary.
    """
    return {
        "H": ["M", "A", "G"],
        "L": ["A", "M"]
    }

@pytest.fixture
def sample_input_filename() -> str:
    """
    Provides a sample input filename.
    """
    return "protein_ABC.pdb"

def test_generate_output_file(temp_output_dir: Path, sample_extracted_chains: dict, sample_input_filename: str, tmp_path: Path):
    """
    Test the generation of the output JSON file with correct schema and content.
    """
    # Override the default output directory for testing.
    generator = OutputFileGenerator(output_dir=temp_output_dir)
    output_path = generator.generate_output_file(sample_input_filename, sample_extracted_chains)

    # Verify that the file exists.
    assert output_path.exists()

    # Load the file and verify its contents.
    with output_path.open("r") as f:
        data = json.load(f)

    # Check that the schema keys are present.
    assert "input_filename" in data
    assert "processed_at" in data
    assert "extracted_chains" in data

    # Validate input filename.
    assert data["input_filename"] == sample_input_filename

    # Validate processed_at is a valid ISO8601 string (basic check).
    try:
        dt = datetime.fromisoformat(data["processed_at"].replace("Z", ""))
    except Exception:
        pytest.fail("processed_at is not a valid ISO8601 timestamp")

    # Validate extracted_chains.
    expected_chains = {
        "H": {
            "sequence": "MAG",
            "length": 3
        },
        "L": {
            "sequence": "AM",
            "length": 2
        }
    }
    assert data["extracted_chains"] == expected_chains

def test_output_file_naming(temp_output_dir: Path, sample_extracted_chains: dict, sample_input_filename: str):
    """
    Test that the output file is named correctly based on the input filename.
    """
    generator = OutputFileGenerator(output_dir=temp_output_dir)
    output_path = generator.generate_output_file(sample_input_filename, sample_extracted_chains)
    expected_filename = "protein_ABC_output.json"
    assert output_path.name == expected_filename
